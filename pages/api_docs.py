# API文档
"""
企业数据智能监控大屏 - API 文档页
展示 Flask RESTful API 接口说明与调用示例
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.navbar import render_navbar, render_sidebar

render_navbar("API文档")
auto_refresh, refresh_interval, _ = render_sidebar()

st.markdown("""
<div style="margin-bottom:16px;">
    <span style="font-size:13px; color:#cbd5e1;">Flask RESTful API | 前后端分离 | 多端复用</span>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown('<div class="panel-header">服务启动</div>', unsafe_allow_html=True)
    st.code("python backend/app.py", language="bash")
    st.markdown("""
    <div style="font-size:12px; color:#cbd5e1; line-height:1.8;">
        默认运行在 <code style="background:rgba(100,180,255,0.1); color:#3b82f6; padding:2px 6px; border-radius:4px;">http://127.0.0.1:5000</code>，
        支持 CORS 跨域。数据自动从 CSV 导入本地 SQLite（首次启动建表），无需额外配置。
        生产环境建议使用 Gunicorn + Nginx 或 Docker 容器化部署。
    </div>
    """, unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:5000"

api_endpoints = [
    {
        "name": "KPI 汇总",
        "method": "GET",
        "path": "/api/kpi",
        "params": [("period", "string", "today / week / month", "统计周期，默认 today")],
        "desc": "获取核心经营指标（销售额、订单量、客单价、付款率、退款率、覆盖省份）及环比变化",
        "example": f"curl \"{BASE_URL}/api/kpi?period=today\"",
        "response": """{
  "sales":   {"value": 15.8, "unit": "万", "change": -17.8, "trend": "down"},
  "orders":  {"value": 2112, "unit": "单", "change": -21.5, "trend": "down"},
  "avg_order": {"value": 86.9, "unit": "元", "change": 6.7, "trend": "up"},
  "pay_rate": {"value": 86.0, "unit": "%", "change": -1.7, "trend": "down"},
  "refund_rate": {"value": 18.2, "unit": "%", "change": -8.5, "trend": "down"},
  "provinces": {"value": 30, "unit": "个", "change": 0.0, "trend": "flat"}
}"""
    },
    {
        "name": "分时趋势",
        "method": "GET",
        "path": "/api/trend",
        "params": [("date", "string", "YYYY-MM-DD", "查询日期，默认今天")],
        "desc": "获取每日销售额 / 订单量 / 付款订单趋势",
        "example": f"curl \"{BASE_URL}/api/trend?date=2026-07-15\"",
        "response": """[
  {"date": "2020-02-01", "sales": 0.70, "orders": 176, "paid": 163},
  {"date": "2020-02-02", "sales": 0.85, "orders": 222, "paid": 199}
]"""
    },
    {
        "name": "渠道占比",
        "method": "GET",
        "path": "/api/channel",
        "params": [("date", "string", "YYYY-MM-DD", "查询日期，默认今天")],
        "desc": "获取订单状态分布（已付款 / 未付款 / 已退款）及占比",
        "example": f"curl \"{BASE_URL}/api/channel?date=2026-07-15\"",
        "response": """[
  {"channel": "已付款", "orders": 18441, "share": 65.8},
  {"channel": "未付款", "orders": 3923, "share": 14.0},
  {"channel": "已退款", "orders": 5646, "share": 20.2}
]"""
    },
    {
        "name": "省份销售",
        "method": "GET",
        "path": "/api/top_products",
        "params": [("date", "string", "YYYY-MM-DD", "查询日期，默认今天")],
        "desc": "获取省份销售 Top10（含订单量与销售额）",
        "example": f"curl \"{BASE_URL}/api/top_products?date=2026-07-15\"",
        "response": """[
  {"province": "上海", "orders": 3353, "revenue_wan": 26.40},
  {"province": "北京", "orders": 2054, "revenue_wan": 16.64}
]"""
    },
    {
        "name": "订单流水",
        "method": "GET",
        "path": "/api/orders_stream",
        "params": [("limit", "int", "1-100", "返回条数，默认 20")],
        "desc": "获取最新订单流水（订单号、时间、金额、状态）",
        "example": f"curl \"{BASE_URL}/api/orders_stream?limit=10\"",
        "response": """[
  {"order_id": "20624", "time": "23:54:32",
   "amount": 160.00, "status": "已付款"},
  {"order_id": "20625", "time": "23:54:23",
   "amount": 114.00, "status": "已付款"}
]"""
    },
]

for idx, api in enumerate(api_endpoints):
    with st.container(border=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <span style="background:rgba(59,130,246,0.15); color:#3b82f6; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:700;">{api['method']}</span>
                <span style="font-size:15px; font-weight:700; color:#f1f5f9;">{api['name']}</span>
            </div>
            <div style="font-size:13px; color:#06b6d4; font-family:monospace; margin-bottom:8px;">{api['path']}</div>
            <div style="font-size:12px; color:#cbd5e1; line-height:1.6; margin-bottom:10px;">{api['desc']}</div>
            """, unsafe_allow_html=True)

            if api['params']:
                st.markdown("<div style='font-size:12px; font-weight:600; color:#e2e8f0; margin-bottom:6px;'>请求参数</div>", unsafe_allow_html=True)
                for p_name, p_type, p_range, p_desc in api['params']:
                    st.markdown(f"""
                    <div style="display:flex; gap:8px; font-size:11px; color:#cbd5e1; margin-bottom:4px;">
                        <span style="color:#3b82f6; font-weight:600; min-width:60px;">{p_name}</span>
                        <span style="color:#cbd5e1;">{p_type}</span>
                        <span style="color:#f59e0b;">{p_range}</span>
                        <span>{p_desc}</span>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='font-size:12px; font-weight:600; color:#e2e8f0; margin:10px 0 6px;'>调用示例</div>", unsafe_allow_html=True)
            st.code(api['example'], language="bash")

        with col2:
            st.markdown("<div style='font-size:12px; font-weight:600; color:#e2e8f0; margin-bottom:6px;'>响应示例</div>", unsafe_allow_html=True)
            st.code(api['response'], language="json")

with st.container(border=True):
    st.markdown('<div class="panel-header">技术栈与部署</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px; color:#cbd5e1; line-height:1.8;">
        <strong style="color:#3b82f6;">后端框架</strong>：Flask 3.x + Flask-CORS<br>
        <strong style="color:#8b5cf6;">数据层</strong>：真实天猫订单成交数据（天池公开数据集，28,010 单）经 Pandas 计算指标<br>
        <strong style="color:#10b981;">前端</strong>：Streamlit 读取同一份数据，前后端分离<br>
        <strong style="color:#f59e0b;">部署方式</strong>：本地开发直接运行 backend/app.py；生产环境建议 Gunicorn 或 Docker<br>
        <strong style="color:#06b6d4;">跨域支持</strong>：默认开启 CORS，第三方系统可直接调用
    </div>
    """, unsafe_allow_html=True)

if auto_refresh:
    import time
    interval_seconds = int(refresh_interval.replace("s", ""))
    time.sleep(interval_seconds)
    st.rerun()
