"""
生成90天电商业务模拟数据
逻辑自洽: 销售额 = 订单量 x 客单价, 渠道占比和为100%, 白天高夜晚低, 周末高工作日低
"""
import csv
import os
import random
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== 基础参数 ==========
END_DATE = datetime(2026, 7, 15)
START_DATE = END_DATE - timedelta(days=90)
ALL_DATES = [START_DATE + timedelta(days=i) for i in range(91)]

CHANNELS = ["小程序", "APP", "线下门店", "第三方平台"]
PRODUCTS = [
    ("无线蓝牙耳机 Pro", 299, "数码"),
    ("智能运动手环 X3", 199, "数码"),
    ("便携充电宝 20000mAh", 89, "数码"),
    ("机械键盘 RGB", 349, "数码"),
    ("护眼台灯 智能版", 159, "家居"),
    ("蓝牙音箱 Mini", 129, "数码"),
    ("手机支架 铝合金", 39, "配件"),
    ("Type-C 数据线套装", 29, "配件"),
    ("桌面收纳盒 多层", 49, "家居"),
    ("USB 扩展坞 7合1", 199, "数码"),
    ("不锈钢保温杯 500ml", 79, "家居"),
    ("电动牙刷 声波款", 259, "家居"),
    ("瑜伽垫 防滑加厚", 69, "运动"),
    ("智能体重秤", 99, "家居"),
    ("筋膜枪 迷你款", 179, "运动"),
]
CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "重庆", "西安"]

# ========== 生成每日KPI汇总 ==========
def generate_daily_kpi():
    rows = []
    for d in ALL_DATES:
        is_weekend = 1 if d.weekday() >= 5 else 0
        day_of_year = d.timetuple().tm_yday

        # 基础值 + 季节性 + 周末效应 + 噪声
        base_order = 4500 + 200 * np.sin(day_of_year / 365 * 2 * np.pi) + is_weekend * 800
        orders = max(200, int(base_order + np.random.normal(0, 200)))

        base_aov = 230 + 10 * np.sin(day_of_year / 365 * 2 * np.pi)
        avg_order = max(180, base_aov + np.random.normal(0, 8))

        sales = round(orders * avg_order / 10000, 2)  # 万元

        base_users = 900 + 100 * np.sin(day_of_year / 365 * 2 * np.pi) + is_weekend * 300
        users = max(100, int(base_users + np.random.normal(0, 80)))

        conversion = round(orders / users * 100, 1) if users > 0 else 0
        conversion = min(50, max(10, conversion + np.random.normal(0, 0.8)))

        repeat = max(20, int(users * (0.12 + 0.03 * is_weekend) + np.random.normal(0, 15)))

        rows.append({
            "date": d.strftime("%Y-%m-%d"),
            "sales_wan": sales,
            "orders": orders,
            "users": users,
            "conversion_pct": conversion,
            "avg_order_yuan": round(avg_order, 1),
            "repeat_users": repeat,
            "is_weekend": is_weekend,
        })
    return rows

# ========== 生成每小时趋势数据 ==========
def generate_hourly_trend():
    rows = []
    for d in ALL_DATES:
        for h in range(24):
            is_weekend = 1 if d.weekday() >= 5 else 0
            # 小时因子: 0-6低, 9-12高, 14-18高, 20-22中高, 其他中等
            if 0 <= h <= 6:
                factor = 0.15 + 0.05 * h
            elif h == 7 or h == 8:
                factor = 0.5 + 0.2 * (h - 7)
            elif 9 <= h <= 11:
                factor = 0.9 + 0.1 * (h - 9)
            elif 12 <= h <= 13:
                factor = 0.7
            elif 14 <= h <= 17:
                factor = 0.85 + 0.05 * (h - 14)
            elif 18 <= h <= 19:
                factor = 0.65
            elif 20 <= h <= 22:
                factor = 0.75 - 0.1 * (h - 20)
            else:
                factor = 0.3

            if is_weekend:
                factor *= 0.85  # 周末分布更均匀

            base_per_hour = 230
            orders = max(1, int(base_per_hour * factor + np.random.normal(0, 15)))
            users = max(3, int(orders * 0.38 + np.random.normal(0, 10)))
            sales = round(orders * (230 + np.random.normal(0, 20)), 2)

            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "hour": h,
                "sales_yuan": max(0, sales),
                "orders": orders,
                "users": users,
            })
    return rows

# ========== 生成每日渠道数据 ==========
def generate_channel_daily():
    rows = []
    for d in ALL_DATES:
        total = 4500 + 200 * np.sin(d.timetuple().tm_yday / 365 * 2 * np.pi)
        if d.weekday() >= 5:
            total += 800
        total = max(500, int(total + np.random.normal(0, 200)))

        shares = np.random.dirichlet([35, 28, 22, 15], 1)[0]
        for ch, share in zip(CHANNELS, shares):
            orders = max(1, int(total * share))
            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "channel": ch,
                "orders": orders,
                "share_pct": round(share * 100, 1),
            })
    return rows

# ========== 生成每日商品销量 ==========
def generate_product_daily():
    rows = []
    # 商品权重 (销量占比)
    weights = [18, 15, 13, 11, 10, 9, 8, 7, 6, 5, 5, 4, 4, 3, 3]
    w_sum = sum(weights)

    for d in ALL_DATES:
        total_orders = 4500 + np.random.normal(0, 300)
        is_weekend = 1 if d.weekday() >= 5 else 0
        total_orders += is_weekend * 800
        total_orders = max(200, int(total_orders))

        # 每天各商品销量有波动但保持比例
        for (name, price, cat), w in zip(PRODUCTS, weights):
            normalized = w / w_sum
            daily_noise = np.random.normal(1.0, 0.08)
            if is_weekend:
                daily_noise *= 1.05
            sales_count = max(1, int(total_orders * normalized * daily_noise))
            revenue = round(sales_count * price / 10000, 2)

            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "product": name,
                "price_yuan": price,
                "category": cat,
                "sales_count": sales_count,
                "revenue_wan": revenue,
            })
    return rows

# ========== 生成订单流水 ==========
def generate_order_stream(n=2000):
    rows = []
    channels = CHANNELS.copy()
    statuses = ["已完成", "配送中", "待发货", "已取消"]
    status_weights = [0.55, 0.20, 0.18, 0.07]

    for i in range(n):
        d = END_DATE - timedelta(days=random.randint(0, 30))
        h = random.randint(8, 23)
        m = random.randint(0, 59)
        s = random.randint(0, 59)
        ts = f"{d.strftime('%Y-%m-%d')} {h:02d}:{m:02d}:{s:02d}"

        channel = random.choice(channels)
        amount = round(random.lognormvariate(5.0, 0.8), 2)
        amount = max(19.9, min(5000, amount))
        status = random.choices(statuses, weights=status_weights)[0]

        rows.append({
            "order_id": f"ORD{d.strftime('%Y%m%d')}{i:06d}",
            "order_time": ts,
            "amount_yuan": amount,
            "channel": channel,
            "status": status,
            "user_city": random.choice(CITIES),
        })
    return sorted(rows, key=lambda x: x["order_time"], reverse=True)


# ========== 保存所有数据 ==========
def save_csv(filename, rows):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {filename}: {len(rows)} rows, {os.path.getsize(path):,} bytes")

if __name__ == "__main__":
    print("生成电商业务模拟数据...")

    daily_kpi = generate_daily_kpi()
    save_csv("sales_daily_kpi.csv", daily_kpi)

    hourly = generate_hourly_trend()
    save_csv("sales_hourly.csv", hourly)

    channel = generate_channel_daily()
    save_csv("sales_channel.csv", channel)

    product = generate_product_daily()
    save_csv("sales_products.csv", product)

    orders = generate_order_stream(2000)
    save_csv("orders_stream.csv", orders)

    print("\n数据生成完毕！共5个CSV文件")
    print(f"日期范围: {START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')} (91天)")
