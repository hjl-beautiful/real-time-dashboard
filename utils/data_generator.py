"""
企业数据监控大屏 - 数据读取层（真实数据版）
数据源: 天猫订单成交数据（天池公开数据集 tmall_order_report.csv，28010 单）
所有指标均基于真实订单计算，无任何模拟 / 合成数据。
"""
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CSV_NAME = "tmall_order_report.csv"


# ========== 加载真实订单数据 ==========
def _normalize_province(s):
    s = str(s).strip()
    s = s.replace("省", "").replace("市", "").replace("自治区", "")
    s = s.replace("维吾尔", "").replace("壮族", "").replace("回族", "")
    s = s.replace("特别行政区", "")
    return s


def _load_orders():
    path = os.path.join(DATA_DIR, CSV_NAME)
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    # 字段: 订单编号, 总金额, 买家实际支付金额, 收货地址, 订单创建时间, 订单付款时间, 退款金额
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
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
    df["paid_amount"] = pd.to_numeric(df["paid_amount"], errors="coerce").fillna(0)
    df["refund_amount"] = pd.to_numeric(df["refund_amount"], errors="coerce").fillna(0)
    df["is_paid"] = df["pay_time"].notna()
    df["is_refund"] = df["refund_amount"] > 0

    def _status(r):
        if r["is_refund"]:
            return "已退款"
        if r["is_paid"]:
            return "已付款"
        return "未付款"

    df["status"] = df.apply(_status, axis=1)
    return df


try:
    ORDERS = _load_orders()
except Exception as e:
    print(f"数据加载警告: {e}")
    ORDERS = pd.DataFrame()


def _daily():
    if ORDERS.empty:
        return pd.DataFrame()
    g = ORDERS.groupby("date").agg(
        gmv=("paid_amount", "sum"),
        orders=("order_id", "count"),
        paid=("is_paid", "sum"),
        refunded=("is_refund", "sum"),
        provinces=("province", "nunique"),
        paid_amt=("paid_amount", "sum"),
    ).reset_index()
    return g.sort_values("date").reset_index(drop=True)


DAILY = _daily()


# ========== KPI ==========
def generate_kpi_data(date_str=None, compare_date_str=None):
    """
    生成 KPI 数据（基于真实订单）。
    date_str / compare_date_str 在数据集日期范围内定位；找不到则取最新一天。
    变化率 = 当日 vs 数据集中前一天（真实日环比）。
    """
    if ORDERS.empty or DAILY.empty:
        return _fallback_kpi()

    dates = list(DAILY["date"])
    if date_str is None or date_str not in dates:
        date_str = dates[-1]
    idx = dates.index(date_str)
    if compare_date_str is None or compare_date_str not in dates:
        compare_date_str = dates[idx - 1] if idx > 0 else date_str

    t = DAILY[DAILY["date"] == date_str].iloc[0]
    p = DAILY[DAILY["date"] == compare_date_str].iloc[0] if compare_date_str != date_str else t

    def make_kpi(value, prev, unit):
        if prev and prev != 0:
            change = round((value - prev) / prev * 100, 1)
        else:
            change = 0.0
        trend = "up" if change > 0 else ("down" if change < 0 else "flat")
        return {"value": round(value, 1), "unit": unit, "change": change, "trend": trend}

    total = int(t["orders"])
    paid = int(t["paid"])
    refunded = int(t["refunded"])
    prev_total = int(p["orders"])
    prev_paid = int(p["paid"])
    prev_refunded = int(p["refunded"])

    return {
        "sales": make_kpi(t["gmv"] / 10000, p["gmv"] / 10000, "万"),
        "orders": make_kpi(total, prev_total, "单"),
        "avg_order": make_kpi(
            t["paid_amt"] / paid if paid else 0,
            p["paid_amt"] / prev_paid if prev_paid else 0,
            "元",
        ),
        "pay_rate": make_kpi(
            paid / total * 100 if total else 0,
            prev_paid / prev_total * 100 if prev_total else 0,
            "%",
        ),
        "refund_rate": make_kpi(
            refunded / total * 100 if total else 0,
            prev_refunded / prev_total * 100 if prev_total else 0,
            "%",
        ),
        "provinces": make_kpi(int(t["provinces"]), int(p["provinces"]), "个"),
    }


def _fallback_kpi():
    if ORDERS.empty:
        return {
            "sales": {"value": 0, "unit": "万", "change": 0, "trend": "flat"},
            "orders": {"value": 0, "unit": "单", "change": 0, "trend": "flat"},
            "avg_order": {"value": 0, "unit": "元", "change": 0, "trend": "flat"},
            "pay_rate": {"value": 0, "unit": "%", "change": 0, "trend": "flat"},
            "refund_rate": {"value": 0, "unit": "%", "change": 0, "trend": "flat"},
            "provinces": {"value": 0, "unit": "个", "change": 0, "trend": "flat"},
        }
    paid_total = ORDERS["paid_amount"].sum()
    n = len(ORDERS)
    paid_n = int(ORDERS["is_paid"].sum())
    return {
        "sales": {"value": round(paid_total / 10000, 1), "unit": "万", "change": 0, "trend": "flat"},
        "orders": {"value": n, "unit": "单", "change": 0, "trend": "flat"},
        "avg_order": {"value": round(paid_total / paid_n, 1) if paid_n else 0, "unit": "元", "change": 0, "trend": "flat"},
        "pay_rate": {"value": round(ORDERS["is_paid"].mean() * 100, 1), "unit": "%", "change": 0, "trend": "flat"},
        "refund_rate": {"value": round(ORDERS["is_refund"].mean() * 100, 1), "unit": "%", "change": 0, "trend": "flat"},
        "provinces": {"value": int(ORDERS["province"].nunique()), "unit": "个", "change": 0, "trend": "flat"},
    }


# ========== 趋势（每日真实序列）==========
def generate_trend_data(hours=24, date_str=None):
    if DAILY.empty:
        return _fallback_trend(hours)
    return pd.DataFrame({
        "时间": DAILY["date"].tolist(),
        "销售额": (DAILY["gmv"] / 10000).round(2).tolist(),
        "订单量": DAILY["orders"].astype(int).tolist(),
        "付款订单": DAILY["paid"].astype(int).tolist(),
    })


def _fallback_trend(hours=24):
    return pd.DataFrame({
        "时间": [f"D{i}" for i in range(hours)],
        "销售额": [0] * hours,
        "订单量": [0] * hours,
        "付款订单": [0] * hours,
    })


# ========== 订单状态分布（替代原“渠道”）==========
def generate_channel_data(date_str=None):
    if ORDERS.empty:
        return pd.DataFrame({"渠道": ["已付款", "未付款", "已退款"], "订单量": [0, 0, 0], "占比": [0, 0, 0]})
    counts = ORDERS["status"].value_counts()
    total = int(counts.sum())
    rows = []
    for name in ["已付款", "未付款", "已退款"]:
        c = int(counts.get(name, 0))
        rows.append({"渠道": name, "订单量": c, "占比": round(c / total * 100, 1) if total else 0})
    return pd.DataFrame(rows)


# ========== 省份销售 TOP10（替代原“热销商品”）==========
def generate_top_products(date_str=None):
    if ORDERS.empty:
        return pd.DataFrame(columns=["商品名称", "销量", "销售额(万)", "环比(%)"])
    g = ORDERS.groupby("province").agg(
        gmv=("paid_amount", "sum"), orders=("order_id", "count")
    ).reset_index().sort_values("gmv", ascending=False).head(10)
    return pd.DataFrame({
        "商品名称": g["province"].tolist(),
        "销量": g["orders"].astype(int).tolist(),
        "销售额(万)": (g["gmv"] / 10000).round(2).tolist(),
        "环比(%)": [0.0] * len(g),
    })


# ========== 全国省份订单分布（地图）==========
def generate_province_distribution():
    if ORDERS.empty:
        return pd.DataFrame(columns=["省份", "订单量", "销售额(万)"])
    g = ORDERS.groupby("province").agg(
        orders=("order_id", "count"), gmv=("paid_amount", "sum")
    ).reset_index().sort_values("orders", ascending=False)
    g = g.rename(columns={"province": "省份", "orders": "订单量"})
    g["销售额(万)"] = (g["gmv"] / 10000).round(2)
    return g[["省份", "订单量", "销售额(万)"]]


# ========== 每日交易健康度趋势 ==========
def generate_health_trend():
    if DAILY.empty:
        return pd.DataFrame()
    return pd.DataFrame({
        "时间": DAILY["date"].tolist(),
        "付款率(%)": (DAILY["paid"] / DAILY["orders"] * 100).round(1).tolist(),
        "退款率(%)": (DAILY["refunded"] / DAILY["orders"] * 100).round(1).tolist(),
    })


# ========== 告警（真实阈值）==========
def generate_alert_data(date_str=None):
    if ORDERS.empty:
        return pd.DataFrame(columns=["time", "type", "level", "value", "status"])
    now = datetime.now().strftime("%H:%M:%S")
    alerts = []

    refund_rate = ORDERS["is_refund"].mean() * 100
    if refund_rate >= 18:
        alerts.append({
            "time": now, "type": "整体退款率预警", "level": "高危",
            "value": f"全量订单退款率 {refund_rate:.1f}%",
            "status": "未处理",
        })

    g = ORDERS.groupby("province").agg(
        orders=("order_id", "count"), refunded=("is_refund", "sum")
    ).reset_index()
    g["rr"] = g["refunded"] / g["orders"] * 100
    for _, r in g.sort_values("rr", ascending=False).head(3).iterrows():
        if r["rr"] >= 15:
            alerts.append({
                "time": now, "type": f"{r['province']} 退款率偏高", "level": "中危",
                "value": f"退款率 {r['rr']:.1f}%（{int(r['refunded'])}/{int(r['orders'])} 单）",
                "status": "未处理",
            })

    unpaid = (~ORDERS["is_paid"]).mean() * 100
    if unpaid >= 12:
        alerts.append({
            "time": now, "type": "未付款占比较高", "level": "低危",
            "value": f"未付款订单占比 {unpaid:.1f}%",
            "status": "处理中",
        })

    if not alerts:
        pay_rate = ORDERS["is_paid"].mean() * 100
        alerts.append({
            "time": now, "type": "数据监控正常", "level": "低危",
            "value": f"整体付款率 {pay_rate:.1f}%",
            "status": "已处理",
        })
    return pd.DataFrame(alerts[:6])


# ========== 订单流水（真实抽样）==========
def generate_order_stream(n=8):
    if ORDERS.empty:
        return pd.DataFrame(columns=["订单编号", "下单时间", "消费金额", "订单状态"])
    pool = ORDERS.sort_values("create_time", ascending=False).head(max(n * 3, 12))
    sample = pool.sample(min(n, len(pool)), random_state=1)
    out = []
    for _, r in sample.iterrows():
        out.append({
            "订单编号": str(r["order_id"]),
            "下单时间": r["create_time"].strftime("%H:%M:%S") if pd.notna(r["create_time"]) else "",
            "消费金额": f"¥{r['paid_amount']:.2f}",
            "订单状态": r["status"],
        })
    return pd.DataFrame(out)


# ========== 付款转化漏斗 ==========
def generate_funnel_data(date_str=None):
    """下单 → 付款 → 完成 的转化漏损（基于真实订单）。"""
    if ORDERS.empty:
        return pd.DataFrame({"阶段": ["总下单", "已付款", "已完成"], "数量": [0, 0, 0]})
    total = len(ORDERS)
    paid = int(ORDERS["is_paid"].sum())
    completed = int((ORDERS["is_paid"] & ~ORDERS["is_refund"]).sum())
    return pd.DataFrame({
        "阶段": ["总下单订单", "已付款订单", "已完成订单"],
        "数量": [total, paid, completed],
    })


# ========== 优惠力度（实付率）==========
def get_overall_discount_rate():
    """整体实付率 = 实付金额 / 总金额（体现平台补贴/折扣深度）。"""
    if ORDERS.empty or ORDERS["total_amount"].sum() == 0:
        return 0.0
    return round(ORDERS["paid_amount"].sum() / ORDERS["total_amount"].sum() * 100, 1)


def generate_discount_data(date_str=None):
    """各省份实付率（Top10 订单量省份）。"""
    if ORDERS.empty:
        return pd.DataFrame({"省份": [], "实付率(%)": []})
    g = ORDERS.groupby("province").agg(
        total=("total_amount", "sum"), paid=("paid_amount", "sum"), orders=("order_id", "count")
    ).reset_index()
    g = g[g["total"] > 0].sort_values("orders", ascending=False).head(10)
    g["实付率(%)"] = (g["paid"] / g["total"] * 100).round(1)
    return pd.DataFrame({"省份": g["province"].tolist(), "实付率(%)": g["实付率(%)"].tolist()})


# ========== 客单价分布 ==========
def generate_price_distribution(date_str=None):
    """已付款订单的客单价（实付金额）分布直方图。"""
    if ORDERS.empty:
        return pd.DataFrame({"区间": [], "订单数": []})
    paid = ORDERS[ORDERS["is_paid"] & (ORDERS["paid_amount"] > 0)]["paid_amount"]
    if paid.empty:
        return pd.DataFrame({"区间": ["无数据"], "订单数": [0]})
    bins = [0, 50, 100, 200, 500, 1000, float("inf")]
    labels = ["0-50", "50-100", "100-200", "200-500", "500-1000", "1000+"]
    cut = pd.cut(paid, bins=bins, labels=labels, right=False)
    counts = cut.value_counts().reindex(labels, fill_value=0)
    return pd.DataFrame({"区间": labels, "订单数": counts.astype(int).tolist()})


# ========== 辅助 ==========
def get_available_dates():
    if DAILY.empty:
        return []
    return list(DAILY["date"])


def _kpi_daily_series(kpi_name):
    if DAILY.empty:
        return pd.DataFrame()
    if kpi_name == "sales":
        vals = (DAILY["gmv"] / 10000).round(2)
    elif kpi_name == "orders":
        vals = DAILY["orders"].astype(int)
    elif kpi_name == "avg_order":
        vals = (DAILY["paid_amt"] / DAILY["paid"].replace(0, np.nan)).round(1)
    elif kpi_name == "pay_rate":
        vals = (DAILY["paid"] / DAILY["orders"] * 100).round(1)
    elif kpi_name == "refund_rate":
        vals = (DAILY["refunded"] / DAILY["orders"] * 100).round(1)
    else:  # provinces
        vals = DAILY["provinces"].astype(int)
    return pd.DataFrame({"时间": DAILY["date"].tolist(), "值": vals.tolist()})


def _kpi_by_province(kpi_name):
    if ORDERS.empty:
        return pd.DataFrame()
    g = ORDERS.groupby("province").agg(
        gmv=("paid_amount", "sum"),
        orders=("order_id", "count"),
        paid=("is_paid", "sum"),
        refunded=("is_refund", "sum"),
    ).reset_index()
    if kpi_name == "sales":
        vals = (g["gmv"] / 10000).round(2)
    elif kpi_name == "orders":
        vals = g["orders"].astype(int)
    elif kpi_name == "avg_order":
        vals = (g["gmv"] / g["paid"].replace(0, np.nan)).round(1)
    elif kpi_name == "pay_rate":
        vals = (g["paid"] / g["orders"] * 100).round(1)
    elif kpi_name == "refund_rate":
        vals = (g["refunded"] / g["orders"] * 100).round(1)
    else:
        vals = pd.Series([1] * len(g))
    return pd.DataFrame({"维度": g["province"].tolist(), "值": vals.tolist()})


def get_kpi_detail(kpi_name, date_str=None):
    return _kpi_daily_series(kpi_name)


def get_kpi_detail_by_dimension(kpi_name, dimension, date_str=None):
    """维度下钻：时间（每日序列）/ 省份 / 订单状态"""
    if dimension == "时间":
        return _kpi_daily_series(kpi_name)
    if dimension == "省份":
        return _kpi_by_province(kpi_name)
    if dimension == "订单状态":
        if ORDERS.empty:
            return pd.DataFrame()
        counts = ORDERS["status"].value_counts()
        return pd.DataFrame({"维度": counts.index.tolist(), "值": counts.values.astype(int).tolist()})
    return pd.DataFrame()
