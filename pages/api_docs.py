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
        "desc": "获取核心经营指标（销售额、订单量、用户、转化率、客单价、复购）及环比变化",
        "example": f"curl \"{BASE_URL}/api/kpi?period=today\"",
        "response": """{
  "sales":   {"value": 128.5, "unit": "万", "change": 23.1, "trend": "up"},
  "orders":  {"value": 5423,  "unit": "单", "change": 14.9, "trend": "up"},
  "users":   {"value": 1742,  "unit": "人", "change": -4.5, "trend": "down"},
  "conversion": {"value": 31.8, "unit": "%", "change": 0.0, "trend": "flat"},
  "avg_order": {"value": 236.8, "unit": "元", "change": 5.2, "trend": "up"},
  "repeat":  {"value": 328,   "unit": "人", "change": -2.1, "trend": "down"}
}"""
    },
    {
        "name": "分时趋势",
        "method": "GET",
        "path": "/api/trend",
        "params": [("date", "string", "YYYY-MM-DD", "查询日期，默认今天")],
        "desc": "获取指定日期 24 小时销售额 / 订单量 / 在线用户趋势",
        "example": f"curl \"{BASE_URL}/api/trend?date=2026-07-15\"",
        "response": """[
  {"hour": "00:00", "sales": 1820.5, "orders": 76, "users": 120},
  {"hour": "12:00", "sales": 5620.0, "orders": 210, "users": 340}
]"""
    },
    {
        "name": "渠道占比",
        "method": "GET",
        "path": "/api/channel",
        "params": [("date", "string", "YYYY-MM-DD", "查询日期，默认今天")],
        "desc": "获取各销售渠道订单量及占比（小程序 / APP / 线下门店 / 第三方平台）",
        "example": f"curl \"{BASE_URL}/api/channel?date=2026-07-15\"",
        "response": """[
  {"channel": "小程序", "orders": 2156, "share": 39.8},
  {"channel": "APP", "orders": 1420, "share": 26.2}
]"""
    },
    {
        "name": "热销商品",
        "method": "GET",
        "path": "/api/top_products",
        "params": [("date", "string", "YYYY-MM-DD", "查询日期，默认今天")],
        "desc": "获取指定日期销量 Top10 商品（含销量与销售额）",
        "example": f"curl \"{BASE_URL}/api/top_products?date=2026-07-15\"",
        "response": """[
  {"product": "无线蓝牙耳机 Pro", "sales_count": 892, "revenue": 26.78, "category": "数码配件"},
  {"product": "智能运动手环 X3", "sales_count": 756, "revenue": 15.12, "category": "智能穿戴"}
]"""
    },
    {
        "name": "准实时订单流",
        "method": "GET",
        "path": "/api/orders_stream",
        "params": [("limit", "int", "1-100", "返回条数，默认 20")],
        "desc": "获取最新订单流水（订单号、时间、金额、渠道、状态、城市）",
        "example": f"curl \"{BASE_URL}/api/orders_stream?limit=10\"",
        "response": """[
  {"order_id": "ORD20260715123456", "time": "14:32:08",
   "amount": 299.0, "channel": "小程序", "status": "已完成", "city": "广州"},
  {"order_id": "ORD20260715123457", "time": "14:30:55",
   "amount": 159.0, "channel": "APP", "status": "配送中", "city": "杭州"}
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
        <strong style="color:#8b5cf6;">数据层</strong>：CSV → SQLite 自动建表导入（91 天自洽业务数据）<br>
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
