"""
企业数据监控大屏 - Flask 后端 API
提供数据查询接口，从CSV/SQLite读取真实业务数据
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DATA_DIR, "dashboard.db")


def init_db():
    """初始化SQLite数据库，从CSV导入"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # KPI日汇总表
    c.execute("""CREATE TABLE IF NOT EXISTS daily_kpi (
        date TEXT PRIMARY KEY,
        sales_wan REAL, orders INTEGER, users INTEGER,
        conversion_pct REAL, avg_order_yuan REAL, repeat_users INTEGER, is_weekend INTEGER
    )""")

    # 小时趋势表
    c.execute("""CREATE TABLE IF NOT EXISTS hourly_trend (
        date TEXT, hour INTEGER, sales_yuan REAL, orders INTEGER, users INTEGER,
        PRIMARY KEY (date, hour)
    )""")

    # 渠道表
    c.execute("""CREATE TABLE IF NOT EXISTS channel_data (
        date TEXT, channel TEXT, orders INTEGER, share_pct REAL,
        PRIMARY KEY (date, channel)
    )""")

    # 商品表
    c.execute("""CREATE TABLE IF NOT EXISTS product_data (
        date TEXT, product TEXT, price_yuan REAL, category TEXT,
        sales_count INTEGER, revenue_wan REAL,
        PRIMARY KEY (date, product)
    )""")

    # 订单流水表
    c.execute("""CREATE TABLE IF NOT EXISTS order_stream (
        order_id TEXT PRIMARY KEY, order_time TEXT, amount_yuan REAL,
        channel TEXT, status TEXT, user_city TEXT
    )""")

    # 导入CSV（如果表为空）
    csv_mappings = {
        "daily_kpi": ("sales_daily_kpi.csv", ["date", "sales_wan", "orders", "users", "conversion_pct", "avg_order_yuan", "repeat_users", "is_weekend"]),
        "hourly_trend": ("sales_hourly.csv", ["date", "hour", "sales_yuan", "orders", "users"]),
        "channel_data": ("sales_channel.csv", ["date", "channel", "orders", "share_pct"]),
        "product_data": ("sales_products.csv", ["date", "product", "price_yuan", "category", "sales_count", "revenue_wan"]),
        "order_stream": ("orders_stream.csv", ["order_id", "order_time", "amount_yuan", "channel", "status", "user_city"]),
    }

    for table, (filename, cols) in csv_mappings.items():
        c.execute(f"SELECT COUNT(*) FROM {table}")
        if c.fetchone()[0] == 0:
            csv_path = os.path.join(DATA_DIR, filename)
            if os.path.exists(csv_path):
                with open(csv_path, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    placeholders = ",".join(["?"] * len(cols))
                    for row in reader:
                        values = [row.get(c, None) for c in cols]
                        try:
                            c.execute(f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) VALUES ({placeholders})", values)
                        except Exception:
                            pass
                conn.commit()

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ========== API 路由 ==========

@app.route("/api/kpi")
def api_kpi():
    """获取KPI汇总数据"""
    period = request.args.get("period", "today")
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if period == "today":
        date_filter = f"date = '{today}'"
        compare_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif period == "week":
        week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_filter = f"date >= '{week_start}'"
        compare_start = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        compare_end = week_start
    elif period == "month":
        month_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        date_filter = f"date >= '{month_start}'"
        compare_start = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        compare_end = month_start
    else:
        date_filter = f"date = '{today}'"
        compare_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 当前周期汇总
    if period == "today":
        row = conn.execute(f"SELECT * FROM daily_kpi WHERE {date_filter}").fetchone()
    else:
        row = conn.execute(f"""
            SELECT 
                '{period}' as date,
                ROUND(AVG(sales_wan), 2) as sales_wan,
                CAST(AVG(orders) AS INTEGER) as orders,
                CAST(AVG(users) AS INTEGER) as users,
                ROUND(AVG(conversion_pct), 1) as conversion_pct,
                ROUND(AVG(avg_order_yuan), 1) as avg_order_yuan,
                CAST(AVG(repeat_users) AS INTEGER) as repeat_users,
                0 as is_weekend
            FROM daily_kpi WHERE {date_filter}
        """).fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "no data"}), 404
    
    # 对比周期（计算变化率）
    if period == "today":
        comp_row = conn.execute(f"SELECT * FROM daily_kpi WHERE date = '{compare_date}'").fetchone()
    else:
        comp_row = conn.execute(f"""
            SELECT
                ROUND(AVG(sales_wan), 2) as sales_wan,
                CAST(AVG(orders) AS INTEGER) as orders,
                CAST(AVG(users) AS INTEGER) as users,
                ROUND(AVG(conversion_pct), 1) as conversion_pct,
                ROUND(AVG(avg_order_yuan), 1) as avg_order_yuan,
                CAST(AVG(repeat_users) AS INTEGER) as repeat_users
            FROM daily_kpi WHERE date >= '{compare_start}' AND date < '{compare_end}'
        """).fetchone() if period != "today" else None
    
    conn.close()
    
    def calc_change(curr, prev, field):
        if not prev:
            return {"value": curr[field], "unit": "", "change": 0.0, "trend": "flat"}
        prev_val = prev[field] if isinstance(prev, dict) else dict(prev)[field]
        if prev_val and prev_val != 0:
            change = round((curr[field] - prev_val) / prev_val * 100, 1)
        else:
            change = 0.0
        trend = "up" if change > 0 else ("down" if change < 0 else "flat")
        
        if field in ("sales_wan",):
            unit = "万"
        elif field in ("orders",):
            unit = "单"
        elif field in ("users", "repeat_users"):
            unit = "人"
        elif field in ("conversion_pct",):
            unit = "%"
        elif field in ("avg_order_yuan",):
            unit = "元"
        else:
            unit = ""
        return {"value": curr[field], "unit": unit, "change": change, "trend": trend}
    
    curr_row = dict(row)
    
    return jsonify({
        "sales": calc_change(curr_row, dict(comp_row) if comp_row else None, "sales_wan"),
        "orders": calc_change(curr_row, dict(comp_row) if comp_row else None, "orders"),
        "users": calc_change(curr_row, dict(comp_row) if comp_row else None, "users"),
        "conversion": calc_change(curr_row, dict(comp_row) if comp_row else None, "conversion_pct"),
        "avg_order": calc_change(curr_row, dict(comp_row) if comp_row else None, "avg_order_yuan"),
        "repeat": calc_change(curr_row, dict(comp_row) if comp_row else None, "repeat_users"),
    })


@app.route("/api/trend")
def api_trend():
    """获取分时趋势"""
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    conn = get_db()
    rows = conn.execute(
        "SELECT hour, sales_yuan, orders, users FROM hourly_trend WHERE date = ? ORDER BY hour",
        (date,)
    ).fetchall()
    conn.close()
    
    return jsonify([{
        "hour": f"{r['hour']:02d}:00",
        "sales": r["sales_yuan"],
        "orders": r["orders"],
        "users": r["users"],
    } for r in rows])


@app.route("/api/channel")
def api_channel():
    """获取渠道数据"""
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    conn = get_db()
    rows = conn.execute(
        "SELECT channel, orders, share_pct FROM channel_data WHERE date = ? ORDER BY orders DESC",
        (date,)
    ).fetchall()
    conn.close()
    return jsonify([{"channel": r["channel"], "orders": r["orders"], "share": r["share_pct"]} for r in rows])


@app.route("/api/top_products")
def api_top_products():
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    conn = get_db()
    rows = conn.execute(
        "SELECT product, sales_count, revenue_wan, category FROM product_data WHERE date = ? ORDER BY sales_count DESC LIMIT 10",
        (date,)
    ).fetchall()
    conn.close()
    return jsonify([{
        "product": r["product"], "sales_count": r["sales_count"],
        "revenue": r["revenue_wan"], "category": r["category"],
    } for r in rows])


@app.route("/api/orders_stream")
def api_orders_stream():
    limit = request.args.get("limit", 20)
    conn = get_db()
    rows = conn.execute(
        "SELECT order_id, order_time, amount_yuan, channel, status, user_city FROM order_stream ORDER BY order_time DESC LIMIT ?",
        (int(limit),)
    ).fetchall()
    conn.close()
    return jsonify([{
        "order_id": r["order_id"], "time": r["order_time"],
        "amount": r["amount_yuan"], "channel": r["channel"],
        "status": r["status"], "city": r["user_city"],
    } for r in rows])


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db()
    print("Flask API 启动: http://localhost:5000")
    app.run(debug=True, port=5000)
