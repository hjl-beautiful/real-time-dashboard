"""
企业数据监控大屏 - Flask 后端 API（真实数据版）
数据源: 天猫订单成交数据（天池公开数据集 tmall_order_report.csv，28010 单）
流程: 读取真实 CSV → Pandas 清洗计算 → 写入本地 SQLite → RESTful 接口对外提供。
前端 Streamlit 可独立运行（直读 CSV）；本后端演示前后端分离与接口复用，指标口径与前端一致，全部基于真实订单，无任何模拟数据。
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sqlite3
import pandas as pd

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DATA_DIR, "dashboard.db")
CSV_NAME = "tmall_order_report.csv"


# ========== 读取并清洗真实订单数据 ==========
def _normalize_province(s):
    s = str(s).strip()
    for token in ("省", "市", "自治区", "维吾尔", "壮族", "回族", "特别行政区"):
        s = s.replace(token, "")
    return s


def _load_orders():
    path = os.path.join(DATA_DIR, CSV_NAME)
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "订单编号": "order_id",
        "总金额": "total_amount",
        "买家实际支付金额": "paid_amount",
        "收货地址": "province",
        "订单创建时间": "create_time",
        "订单付款时间": "pay_time",
        "退款金额": "refund_amount",
    })
    df["province"] = df["province"].apply(_normalize_province)
    df["create_time"] = pd.to_datetime(df["create_time"], errors="coerce")
    df["pay_time"] = pd.to_datetime(
        df["pay_time"].astype(str).str.strip().replace("nan", ""), errors="coerce"
    )
    df["date"] = df["create_time"].dt.date.astype(str)
    for col in ("total_amount", "paid_amount", "refund_amount"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["is_paid"] = df["pay_time"].notna()
    df["is_refund"] = df["refund_amount"] > 0
    df["status"] = df.apply(
        lambda r: "已退款" if r["is_refund"] else ("已付款" if r["is_paid"] else "未付款"),
        axis=1,
    )
    return df


# ========== 初始化 SQLite（从真实数据构建聚合表）==========
def init_db():
    df = _load_orders()
    conn = sqlite3.connect(DB_PATH)

    if df.empty:
        conn.close()
        return

    # 每日 KPI 聚合表
    daily = df.groupby("date").agg(
        gmv=("paid_amount", "sum"),
        orders=("order_id", "count"),
        paid=("is_paid", "sum"),
        refunded=("is_refund", "sum"),
        provinces=("province", "nunique"),
    ).reset_index().sort_values("date")
    daily["gmv_wan"] = (daily["gmv"] / 10000).round(2)
    daily["paid_amt"] = daily["gmv"].round(2)
    daily[["date", "gmv_wan", "orders", "paid", "refunded", "provinces", "paid_amt"]].to_sql(
        "daily_kpi", conn, if_exists="replace", index=False
    )

    # 订单状态分布表
    status_counts = df["status"].value_counts()
    total = int(status_counts.sum())
    status_rows = [{
        "status": name,
        "orders": int(status_counts.get(name, 0)),
        "share": round(int(status_counts.get(name, 0)) / total * 100, 1) if total else 0,
    } for name in ["已付款", "未付款", "已退款"]]
    pd.DataFrame(status_rows).to_sql("order_status", conn, if_exists="replace", index=False)

    # 省份销售表
    prov = df.groupby("province").agg(
        orders=("order_id", "count"), gmv=("paid_amount", "sum")
    ).reset_index().sort_values("gmv", ascending=False)
    prov["revenue_wan"] = (prov["gmv"] / 10000).round(2)
    prov[["province", "orders", "revenue_wan"]].to_sql(
        "province_sales", conn, if_exists="replace", index=False
    )

    # 订单流水表（真实订单，按下单时间倒序）
    stream = df.sort_values("create_time", ascending=False).head(200).copy()
    stream["order_time"] = stream["create_time"].dt.strftime("%H:%M:%S")
    stream[["order_id", "order_time", "paid_amount", "status"]].to_sql(
        "order_stream", conn, if_exists="replace", index=False
    )

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _latest_date(conn):
    row = conn.execute("SELECT MAX(date) AS d FROM daily_kpi").fetchone()
    return row["d"] if row and row["d"] else None


# ========== API 路由 ==========
@app.route("/api/kpi")
def api_kpi():
    """核心经营指标（销售额/订单量/客单价/付款率/退款率/覆盖省份）及真实日环比。

    period=today 取数据集最新一天 vs 前一天；week/month 取尾部窗口均值。
    """
    period = request.args.get("period", "today")
    conn = get_db()
    dates = [r["date"] for r in conn.execute("SELECT date FROM daily_kpi ORDER BY date").fetchall()]
    if not dates:
        conn.close()
        return jsonify({"error": "no data"}), 404

    def row_of(d):
        return conn.execute("SELECT * FROM daily_kpi WHERE date = ?", (d,)).fetchone()

    if period in ("week", "month"):
        win = 7 if period == "week" else 30
        cur_dates = dates[-win:]
        prev_dates = dates[-2 * win:-win] if len(dates) >= 2 * win else []
        cur = _agg_window(conn, cur_dates)
        prev = _agg_window(conn, prev_dates) if prev_dates else None
    else:
        cur = dict(row_of(dates[-1]))
        prev = dict(row_of(dates[-2])) if len(dates) >= 2 else None
    conn.close()

    def kpi(cur_val, prev_val, unit):
        if prev_val and prev_val != 0:
            change = round((cur_val - prev_val) / prev_val * 100, 1)
        else:
            change = 0.0
        trend = "up" if change > 0 else ("down" if change < 0 else "flat")
        return {"value": round(cur_val, 1), "unit": unit, "change": change, "trend": trend}

    def metrics(r):
        o = r["orders"] or 0
        paid = r["paid"] or 0
        refunded = r["refunded"] or 0
        return {
            "sales": r["gmv_wan"],
            "orders": o,
            "avg_order": (r["paid_amt"] / paid) if paid else 0,
            "pay_rate": (paid / o * 100) if o else 0,
            "refund_rate": (refunded / o * 100) if o else 0,
            "provinces": r["provinces"],
        }

    c = metrics(cur)
    p = metrics(prev) if prev else {k: 0 for k in c}
    return jsonify({
        "sales": kpi(c["sales"], p["sales"], "万"),
        "orders": kpi(c["orders"], p["orders"], "单"),
        "avg_order": kpi(c["avg_order"], p["avg_order"], "元"),
        "pay_rate": kpi(c["pay_rate"], p["pay_rate"], "%"),
        "refund_rate": kpi(c["refund_rate"], p["refund_rate"], "%"),
        "provinces": kpi(c["provinces"], p["provinces"], "个"),
    })


def _agg_window(conn, date_list):
    """对一组日期做窗口聚合，返回与 daily_kpi 同结构的 dict。"""
    if not date_list:
        return {"gmv_wan": 0, "orders": 0, "paid": 0, "refunded": 0, "provinces": 0, "paid_amt": 0}
    placeholders = ",".join(["?"] * len(date_list))
    row = conn.execute(
        f"""SELECT ROUND(SUM(gmv_wan),2) AS gmv_wan, SUM(orders) AS orders,
                   SUM(paid) AS paid, SUM(refunded) AS refunded,
                   MAX(provinces) AS provinces, ROUND(SUM(paid_amt),2) AS paid_amt
            FROM daily_kpi WHERE date IN ({placeholders})""",
        date_list,
    ).fetchone()
    return dict(row)


@app.route("/api/trend")
def api_trend():
    """每日销售额 / 订单量 / 付款订单趋势（真实序列）。"""
    conn = get_db()
    rows = conn.execute(
        "SELECT date, gmv_wan, orders, paid FROM daily_kpi ORDER BY date"
    ).fetchall()
    conn.close()
    return jsonify([{
        "date": r["date"],
        "sales": r["gmv_wan"],
        "orders": r["orders"],
        "paid": r["paid"],
    } for r in rows])


@app.route("/api/channel")
def api_channel():
    """订单状态分布（已付款 / 未付款 / 已退款）及占比。"""
    conn = get_db()
    rows = conn.execute(
        "SELECT status, orders, share FROM order_status"
    ).fetchall()
    conn.close()
    return jsonify([
        {"channel": r["status"], "orders": r["orders"], "share": r["share"]} for r in rows
    ])


@app.route("/api/top_products")
def api_top_products():
    """省份销售 Top10（订单量与销售额）。"""
    limit = int(request.args.get("limit", 10))
    conn = get_db()
    rows = conn.execute(
        "SELECT province, orders, revenue_wan FROM province_sales ORDER BY revenue_wan DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return jsonify([
        {"province": r["province"], "orders": r["orders"], "revenue_wan": r["revenue_wan"]}
        for r in rows
    ])


@app.route("/api/orders_stream")
def api_orders_stream():
    """最新订单流水（订单号 / 时间 / 金额 / 状态）。"""
    limit = int(request.args.get("limit", 20))
    conn = get_db()
    rows = conn.execute(
        "SELECT order_id, order_time, paid_amount, status FROM order_stream LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return jsonify([{
        "order_id": str(r["order_id"]),
        "time": r["order_time"],
        "amount": round(r["paid_amount"], 2),
        "status": r["status"],
    } for r in rows])


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db()
    print("Flask API 启动: http://localhost:5000  (数据源: 天猫订单成交数据 28010 单)")
    app.run(debug=True, port=5000)
