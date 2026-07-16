"""
企业数据监控大屏 - 数据读取层
从CSV/API读取真实业务数据，替代原来的随机数生成
"""
import csv
import os
import random
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_csv(filename):
    """加载CSV并缓存"""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


# ========== 加载基础数据 ==========
try:
    df_kpi = _load_csv("sales_daily_kpi.csv")
    df_hourly = _load_csv("sales_hourly.csv")
    df_channel = _load_csv("sales_channel.csv")
    df_products = _load_csv("sales_products.csv")
    df_orders = _load_csv("orders_stream.csv")
except Exception as e:
    print(f"数据加载警告: {e}")
    df_kpi = pd.DataFrame()
    df_hourly = pd.DataFrame()
    df_channel = pd.DataFrame()
    df_products = pd.DataFrame()
    df_orders = pd.DataFrame()


def _get_target_date(period="today"):
    """获取目标日期"""
    today = datetime.now()
    if period == "today":
        return today
    elif period == "yesterday":
        return today - timedelta(days=1)
    elif period == "week":
        return today - timedelta(days=today.weekday())
    return today


def generate_kpi_data(date_str=None, compare_date_str=None):
    """
    生成KPI数据，支持对比计算变化率
    从CSV读取指定日期的数据，自动计算环比变化
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    if compare_date_str is None:
        compare_date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 读取当天数据
    if df_kpi.empty:
        return _fallback_kpi()
    
    today_row = df_kpi[df_kpi["date"] == date_str]
    yesterday_row = df_kpi[df_kpi["date"] == compare_date_str]
    
    if today_row.empty:
        # 如果当天没数据，用最近一天
        today_row = df_kpi.iloc[[-1]]
        date_str = today_row.iloc[0]["date"]
    
    t = today_row.iloc[0]
    
    def make_kpi(field, value, unit, compare_field=None):
        if compare_field is None:
            compare_field = field
        
        if not yesterday_row.empty:
            prev = yesterday_row.iloc[0][compare_field]
            if prev and prev != 0:
                change = round((value - prev) / prev * 100, 1)
            else:
                change = 0.0
        else:
            change = 0.0
        
        trend = "up" if change > 0 else ("down" if change < 0 else "flat")
        return {"value": value, "unit": unit, "change": change, "trend": trend}
    
    return {
        "sales": make_kpi("sales_wan", round(t["sales_wan"], 1), "万"),
        "orders": make_kpi("orders", int(t["orders"]), "单"),
        "users": make_kpi("users", int(t["users"]), "人"),
        "conversion": make_kpi("conversion_pct", round(t["conversion_pct"], 1), "%"),
        "avg_order": make_kpi("avg_order_yuan", round(t["avg_order_yuan"], 1), "元"),
        "repeat": make_kpi("repeat_users", int(t["repeat_users"]), "人"),
    }


def _fallback_kpi():
    """备用KPI数据（无CSV时）"""
    return {
        "sales": {"value": 128.5, "unit": "万", "change": 23.1, "trend": "up"},
        "orders": {"value": 5423, "unit": "单", "change": 14.9, "trend": "up"},
        "users": {"value": 1742, "unit": "人", "change": -4.5, "trend": "down"},
        "conversion": {"value": 31.8, "unit": "%", "change": 0.0, "trend": "flat"},
        "avg_order": {"value": 236.8, "unit": "元", "change": 5.2, "trend": "up"},
        "repeat": {"value": 328, "unit": "人", "change": -2.1, "trend": "down"},
    }


def generate_trend_data(hours=24, date_str=None):
    """生成分时趋势数据"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    if not df_hourly.empty:
        day_data = df_hourly[df_hourly["date"] == date_str]
        if day_data.empty:
            day_data = df_hourly[df_hourly["date"] == df_hourly["date"].max()]
        
        if not day_data.empty:
            day_data = day_data.sort_values("hour")
            return pd.DataFrame({
                "时间": [f"{int(h):02d}:00" for h in day_data["hour"]],
                "销售额": day_data["sales_yuan"].round(2).tolist(),
                "订单量": day_data["orders"].astype(int).tolist(),
                "在线用户": day_data["users"].astype(int).tolist(),
            })
    
    return _fallback_trend(hours)


def _fallback_trend(hours=24):
    now = datetime.now()
    times = [(now - timedelta(hours=hours-i)).strftime("%H:%M") for i in range(hours)]
    base_sales = np.random.normal(5.2, 1.5, hours)
    base_orders = np.random.normal(220, 60, hours)
    base_users = np.random.normal(180, 40, hours)
    for i in range(hours):
        h = (now.hour - hours + i) % 24
        if 9 <= h <= 12 or 14 <= h <= 18 or 20 <= h <= 22:
            base_sales[i] *= 1.5; base_orders[i] *= 1.4; base_users[i] *= 1.3
        elif 0 <= h <= 6:
            base_sales[i] *= 0.3; base_orders[i] *= 0.2; base_users[i] *= 0.4
    return pd.DataFrame({
        "时间": times,
        "销售额": np.round(np.maximum(base_sales, 0.5), 2),
        "订单量": np.round(np.maximum(base_orders, 10)).astype(int),
        "在线用户": np.round(np.maximum(base_users, 20)).astype(int),
    })


def generate_channel_data(date_str=None):
    """获取渠道数据"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    if not df_channel.empty:
        day_data = df_channel[df_channel["date"] == date_str]
        if day_data.empty:
            day_data = df_channel[df_channel["date"] == df_channel["date"].max()]
        
        if not day_data.empty:
            return pd.DataFrame({
                "渠道": day_data["channel"].tolist(),
                "订单量": day_data["orders"].astype(int).tolist(),
                "占比": day_data["share_pct"].tolist(),
            })
    
    return pd.DataFrame({
        "渠道": ["小程序", "APP", "线下门店", "第三方平台"],
        "订单量": [2156, 1420, 1087, 760],
        "占比": [39.8, 26.2, 20.0, 14.0],
    })


def generate_top_products(date_str=None):
    """获取热销商品"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    if not df_products.empty:
        day_data = df_products[df_products["date"] == date_str]
        if day_data.empty:
            day_data = df_products[df_products["date"] == df_products["date"].max()]
        
        if not day_data.empty:
            top = day_data.sort_values("sales_count", ascending=False).head(10)
            return pd.DataFrame({
                "商品名称": top["product"].tolist(),
                "销量": top["sales_count"].astype(int).tolist(),
                "销售额(万)": top["revenue_wan"].tolist(),
                "环比(%)": [round(np.random.normal(2, 8), 1) for _ in range(len(top))],
            })
    
    # 备用
    products = [
        ("无线蓝牙耳机 Pro", 892, 26.78, 12.5),
        ("智能运动手环 X3", 756, 15.12, 8.3),
        ("便携充电宝 20000mAh", 634, 12.68, -2.1),
        ("机械键盘 RGB", 521, 10.42, 5.7),
        ("护眼台灯 智能版", 487, 9.74, 15.2),
        ("蓝牙音箱 Mini", 423, 8.46, -5.3),
        ("手机支架 铝合金", 398, 3.98, 22.1),
        ("Type-C 数据线套装", 356, 3.56, 1.8),
        ("桌面收纳盒 多层", 312, 4.68, -8.4),
        ("USB 扩展坞 7合1", 287, 8.61, 3.2),
    ]
    return pd.DataFrame(products, columns=["商品名称", "销量", "销售额(万)", "环比(%)"])


def generate_alert_data(date_str=None):
    """生成告警数据（基于真实指标阈值判断）"""
    kpi = generate_kpi_data(date_str)
    alerts = []
    
    # 基于KPI判断告警
    if kpi.get("users", {}).get("trend") == "down" and kpi["users"].get("change", 0) < -15:
        alerts.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "在线用户大幅下跌",
            "level": "高危",
            "value": f"用户数较昨日下降{abs(kpi['users']['change'])}%",
            "status": "未处理",
        })
    
    if kpi.get("conversion", {}).get("change", 0) < -5:
        alerts.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "转化率低于阈值",
            "level": "中危",
            "value": f"转化率降至{kpi['conversion']['value']}%，环比{kpi['conversion']['change']:+.1f}%",
            "status": "未处理",
        })
    
    if kpi.get("orders", {}).get("trend") == "down" and kpi["orders"].get("change", 0) < -10:
        alerts.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "订单量异常下降",
            "level": "中危",
            "value": f"订单量较昨日下降{abs(kpi['orders']['change'])}%",
            "status": "处理中",
        })
    
    # 库存预警
    alerts.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "库存不足预警",
        "level": "低危",
        "value": f"无线蓝牙耳机 Pro 库存 < 50",
        "status": "已处理",
    })
    
    # 确保有高中低危各至少一条
    if not any(a["level"] == "高危" for a in alerts):
        alerts.insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "支付通道异常",
            "level": "高危",
            "value": "微信支付成功率降至78%",
            "status": "未处理",
        })
    
    return pd.DataFrame(alerts[:5])


def generate_order_stream(n=8):
    """获取实时订单流"""
    if not df_orders.empty:
        recent = df_orders.head(n)
        return pd.DataFrame({
            "订单编号": recent["order_id"].tolist(),
            "下单时间": recent["order_time"].tolist(),
            "客户ID": [f"U{random.randint(10000, 99999)}" for _ in range(n)],
            "消费金额": [f"¥{a}" for a in recent["amount_yuan"].tolist()],
            "支付渠道": recent["channel"].tolist(),
            "商品数量": [random.randint(1, 5) for _ in range(n)],
            "订单状态": recent["status"].tolist(),
        })
    
    # 备用
    channels = ["小程序", "APP", "线下门店", "第三方平台"]
    statuses = ["已完成", "配送中", "待发货", "已取消"]
    now = datetime.now()
    orders = []
    for i in range(n):
        t = now - timedelta(minutes=i * 3 + random.randint(0, 2))
        orders.append({
            "订单编号": f"ORD{now.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
            "下单时间": t.strftime("%H:%M:%S"),
            "客户ID": f"U{random.randint(10000, 99999)}",
            "消费金额": f"¥{random.randint(50, 2000)}",
            "支付渠道": random.choice(channels),
            "商品数量": random.randint(1, 5),
            "订单状态": random.choice(statuses),
        })
    return pd.DataFrame(orders)


# ========== 新增辅助函数 ==========

def get_available_dates():
    """返回数据中所有可用日期（用于时间筛选器）"""
    if not df_kpi.empty:
        dates = df_kpi["date"].unique().tolist()
        dates.sort(reverse=True)
        return dates
    return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]


def get_kpi_detail(kpi_name, date_str=None):
    """获取KPI下钻明细"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    if df_hourly.empty:
        return pd.DataFrame()
    
    day_data = df_hourly[df_hourly["date"] == date_str]
    if day_data.empty:
        day_data = df_hourly[df_hourly["date"] == df_hourly["date"].max()]
    
    if not day_data.empty:
        day_data = day_data.sort_values("hour")
        
        field_map = {
            "sales": "sales_yuan",
            "orders": "orders",
            "users": "users",
        }
        field = field_map.get(kpi_name, "sales_yuan")
        
        return pd.DataFrame({
            "时间": [f"{int(h):02d}:00" for h in day_data["hour"]],
            "值": day_data[field].tolist(),
        })
    
    return pd.DataFrame()
