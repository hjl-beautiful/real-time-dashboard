import numpy as np
from datetime import datetime, timedelta

def generate_kpi_data(minutes=30):
    now = datetime.now()
    times = [(now - timedelta(minutes=i)).strftime("%H:%M") for i in range(minutes, 0, -1)]

    np.random.seed(42)
    sales = [100 + np.random.randint(-20, 30) for _ in range(minutes)]
    orders = [50 + np.random.randint(-10, 15) for _ in range(minutes)]
    users = [200 + np.random.randint(-30, 40) for _ in range(minutes)]

    return times, sales, orders, users
