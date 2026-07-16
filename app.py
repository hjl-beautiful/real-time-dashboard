import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="企业数据监控大屏",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #4a4a6a;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .kpi-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    .kpi-change {
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }
    .alert-card {
        background: #fff0f0;
        border-left: 4px solid #ff4757;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .normal-card {
        background: #f0fff4;
        border-left: 4px solid #2ed573;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">企业数据监控大屏</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Enterprise Data Monitoring Dashboard</div>', unsafe_allow_html=True)

np.random.seed(42)

now = datetime.now()
times = [(now - timedelta(minutes=i)).strftime("%H:%M") for i in range(30, 0, -1)]

sales = [100 + np.random.randint(-20, 30) for _ in range(30)]
orders = [50 + np.random.randint(-10, 15) for _ in range(30)]
users = [200 + np.random.randint(-30, 40) for _ in range(30)]

col1, col2, col3, col4 = st.columns(4)
with col1:
    current_sales = sales[-1]
    prev_sales = sales[-2]
    change = ((current_sales - prev_sales) / prev_sales) * 100
    color = "#2ed573" if change >= 0 else "#ff4757"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">¥{current_sales}万</div>
            <div class="kpi-label">实时销售额</div>
            <div class="kpi-change" style="color:{color}">{'+' if change >= 0 else ''}{change:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    current_orders = orders[-1]
    prev_orders = orders[-2]
    change = ((current_orders - prev_orders) / prev_orders) * 100
    color = "#2ed573" if change >= 0 else "#ff4757"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{current_orders}</div>
            <div class="kpi-label">实时订单量</div>
            <div class="kpi-change" style="color:{color}">{'+' if change >= 0 else ''}{change:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    current_users = users[-1]
    prev_users = users[-2]
    change = ((current_users - prev_users) / prev_users) * 100
    color = "#2ed573" if change >= 0 else "#ff4757"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{current_users}</div>
            <div class="kpi-label">在线用户数</div>
            <div class="kpi-change" style="color:{color}">{'+' if change >= 0 else ''}{change:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    conversion = round((current_orders / current_users) * 100, 1)
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{conversion}%</div>
            <div class="kpi-label">转化率</div>
            <div class="kpi-change" style="color:#2ed573">正常</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

st.markdown("### 核心指标趋势")

fig, axes = plt.subplots(1, 3, figsize=(18, 4.5))

axes[0].plot(times, sales, color='#667eea', linewidth=2, marker='o', markersize=4)
axes[0].fill_between(times, sales, alpha=0.2, color='#667eea')
axes[0].set_title('销售额趋势', fontsize=12, fontweight='bold', pad=10)
axes[0].set_ylabel('万元')
axes[0].grid(True, alpha=0.3)
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)
axes[0].tick_params(axis='x', rotation=45)

axes[1].plot(times, orders, color='#764ba2', linewidth=2, marker='s', markersize=4)
axes[1].fill_between(times, orders, alpha=0.2, color='#764ba2')
axes[1].set_title('订单量趋势', fontsize=12, fontweight='bold', pad=10)
axes[1].set_ylabel('单')
axes[1].grid(True, alpha=0.3)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)
axes[1].tick_params(axis='x', rotation=45)

axes[2].plot(times, users, color='#f093fb', linewidth=2, marker='^', markersize=4)
axes[2].fill_between(times, users, alpha=0.2, color='#f093fb')
axes[2].set_title('在线用户数趋势', fontsize=12, fontweight='bold', pad=10)
axes[2].set_ylabel('人')
axes[2].grid(True, alpha=0.3)
axes[2].spines['top'].set_visible(False)
axes[2].spines['right'].set_visible(False)
axes[2].tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig)

st.markdown("---")

st.markdown("### 实时监控告警")

alerts = []
if current_sales < 85:
    alerts.append(("销售额低于阈值", "warning"))
if current_orders < 40:
    alerts.append(("订单量异常下降", "danger"))
if current_users < 170:
    alerts.append(("在线用户不足", "warning"))

if alerts:
    for msg, level in alerts:
        if level == "danger":
            st.markdown(f'<div class="alert-card"><strong>严重告警：</strong>{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-card" style="border-left-color:#ffa502;"><strong>警告：</strong>{msg}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="normal-card"><strong>系统状态：</strong>所有指标正常运行</div>', unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 数据导出")

df_export = pd.DataFrame({
    "时间": times,
    "销售额(万)": sales,
    "订单量": orders,
    "在线用户": users
})

col1, col2 = st.columns(2)
with col1:
    st.dataframe(df_export.tail(10), use_container_width=True, hide_index=True)
with col2:
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="下载报表 (CSV)",
        data=csv,
        file_name=f"监控数据_{now.strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
