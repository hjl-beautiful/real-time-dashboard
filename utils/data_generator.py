import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_kpi_data():
    """生成核心KPI数据"""
    return {
        "sales": {"value": 128.5, "unit": "万", "change": 23.1, "trend": "up"},
        "orders": {"value": 5423, "unit": "单", "change": 14.9, "trend": "up"},
        "users": {"value": 1742, "unit": "人", "change": -4.5, "trend": "down"},
        "conversion": {"value": 31.8, "unit": "%", "change": 0.0, "trend": "flat"},
        "avg_order": {"value": 236.8, "unit": "元", "change": 5.2, "trend": "up"},
        "repeat": {"value": 328, "unit": "人", "change": -2.1, "trend": "down"},
    }

def generate_trend_data(hours=24):
    """生成分时趋势数据"""
    now = datetime.now()
    times = [(now - timedelta(hours=hours-i)).strftime("%H:%M") for i in range(hours)]

    base_sales = np.random.normal(5.2, 1.5, hours)
    base_orders = np.random.normal(220, 60, hours)
    base_users = np.random.normal(180, 40, hours)

    for i in range(hours):
        h = (now.hour - hours + i) % 24
        if 9 <= h <= 12 or 14 <= h <= 18 or 20 <= h <= 22:
            base_sales[i] *= 1.5
            base_orders[i] *= 1.4
            base_users[i] *= 1.3
        elif 0 <= h <= 6:
            base_sales[i] *= 0.3
            base_orders[i] *= 0.2
            base_users[i] *= 0.4

    return pd.DataFrame({
        "时间": times,
        "销售额": np.round(np.maximum(base_sales, 0.5), 2),
        "订单量": np.round(np.maximum(base_orders, 10)).astype(int),
        "在线用户": np.round(np.maximum(base_users, 20)).astype(int),
    })

def generate_channel_data():
    """生成渠道订单占比数据"""
    return pd.DataFrame({
        "渠道": ["小程序", "APP", "线下门店", "第三方平台"],
        "订单量": [2156, 1420, 1087, 760],
        "占比": [39.8, 26.2, 20.0, 14.0],
    })

def generate_top_products():
    """生成热销商品TOP10"""
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

def generate_alert_data():
    """生成告警数据"""
    alerts = [
        {"time": "09:42:18", "type": "在线用户下跌", "level": "高危", "value": "用户数连续30分钟低于基线20%", "status": "未处理"},
        {"time": "09:38:05", "type": "支付成功率低", "level": "中危", "value": "支付成功率降至 87.3%", "status": "处理中"},
        {"time": "09:25:33", "type": "库存不足预警", "level": "低危", "value": "无线蓝牙耳机 Pro 库存 < 50", "status": "已处理"},
        {"time": "09:15:47", "type": "订单转化率异常", "level": "中危", "value": "转化率跌至 24.1%，低于阈值", "status": "未处理"},
        {"time": "09:08:22", "type": "服务器响应慢", "level": "低危", "value": "API平均响应时间 2.8s", "status": "已处理"},
    ]
    return pd.DataFrame(alerts)

def generate_order_stream():
    """生成实时订单流水"""
    channels = ["小程序", "APP", "线下门店", "第三方平台"]
    statuses = ["已完成", "配送中", "待发货", "已取消"]
    now = datetime.now()
    orders = []
    for i in range(8):
        t = now - timedelta(minutes=i*3 + random.randint(0, 2))
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

def generate_map_data():
    """生成全国用户分布数据"""
    provinces = [
        ("广东", 2850), ("浙江", 1920), ("江苏", 1780), ("北京", 1540), ("上海", 1460),
        ("四川", 1120), ("山东", 1080), ("福建", 950), ("湖北", 870), ("河南", 820),
        ("湖南", 780), ("安徽", 720), ("河北", 680), ("陕西", 620), ("重庆", 580),
        ("辽宁", 520), ("云南", 480), ("江西", 450), ("广西", 420), ("山西", 380),
    ]
    return pd.DataFrame(provinces, columns=["省份", "活跃用户"])
