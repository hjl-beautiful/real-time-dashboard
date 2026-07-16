"""
企业数据智能监控大屏 - 共享导航栏组件
统一所有页面的导航栏、标题栏和动态刷新功能（与「景区客流预测平台」视觉风格一致）
"""
import streamlit as st
import time
from datetime import datetime, timedelta

def render_navbar(current_page: str = "监控总览"):
    """
    渲染统一的顶部标题栏（固定页面标题 + 准实时指示器 + 时间戳）
    current_page: 当前页面名称（用于高亮）
    """
    st.set_page_config(
        page_title="企业数据智能监控大屏",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 全局深色主题 + 统一视觉语言
    st.markdown("""
    <style>
        /* 强制全局深色背景（与景区预测平台一致） */
        .stApp {
            background: linear-gradient(135deg, #0a1628 0%, #0f2642 50%, #0a1628 100%) !important;
        }
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
        }

        /* 全局文字颜色提升可读性 */
        .main .stMarkdown p, .main .stMarkdown li, .main .stMarkdown div {
            color: #e2e8f0;
        }
        .main [data-testid="stExpander"] > div:first-child {
            color: #e2e8f0 !important;
        }
        .main label, .main .stSelectbox label, .main .stSlider label, .main .stToggle label {
            color: #e2e8f0 !important;
        }

        /* 修复侧边栏背景与控件标签 */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111d32 0%, #0d1e36 100%) !important;
            border-right: 1px solid rgba(100, 180, 255, 0.15) !important;
        }
        [data-testid="stSidebar"] .stMarkdown {
            color: #e2e8f0 !important;
        }
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stSlider label,
        [data-testid="stSidebar"] .stToggle label,
        [data-testid="stSidebar"] .stCheckbox label,
        [data-testid="stSidebar"] .stRadio label {
            color: #e2e8f0 !important;
            font-weight: 500 !important;
        }
        [data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
            color: #94a3b8 !important;
        }

        /* 隐藏 Streamlit 默认页面导航 */
        [data-testid="stSidebarNav"] { display: none !important; }

        /* Streamlit container border=True 的深色背景覆盖 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, rgba(13,30,54,0.95) 0%, rgba(8,18,34,0.98) 100%) !important;
            border: 1px solid rgba(100, 180, 255, 0.12) !important;
            border-radius: 16px !important;
            padding: 4px 16px 14px 16px !important;
            margin-bottom: 6px !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            border: none !important;
            box-shadow: none !important;
        }

        /* 面板卡片标题 */
        .panel-header {
            font-size: 16px;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(100, 180, 255, 0.08);
        }

        /* 统计卡片（KPI 概览） */
        .stat-card {
            background: linear-gradient(145deg, rgba(15,38,66,0.9) 0%, rgba(10,22,40,0.95) 100%);
            border: 1px solid rgba(100,180,255,0.08);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3b82f6, #06b6d4);
            border-radius: 12px 12px 0 0;
        }
        .stat-value {
            font-size: 26px;
            font-weight: 800;
            color: #f1f5f9;
            margin-top: 4px;
        }
        .stat-label {
            font-size: 12px;
            color: #cbd5e1;
            margin-top: 4px;
        }
        .stat-change { font-size: 12px; font-weight: 600; margin-top: 4px; }
        .stat-change.up { color: #34d399; }
        .stat-change.down { color: #f87171; }
        .stat-change.flat { color: #94a3b8; }

        /* 顶部固定标题栏 */
        .top-header {
            background: linear-gradient(90deg, rgba(15,38,66,0.95) 0%, rgba(10,22,40,0.95) 100%);
            border: 1px solid rgba(100, 180, 255, 0.1);
            border-radius: 12px;
            padding: 16px 24px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .top-header-title {
            font-size: 22px;
            font-weight: 800;
            color: #f1f5f9;
        }
        .top-header-subtitle {
            font-size: 12px;
            color: #cbd5e1;
        }
        .top-header-nav {
            display: flex;
            gap: 8px;
        }
        .nav-link {
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            color: #cbd5e1;
            background: rgba(100, 180, 255, 0.05);
            border: 1px solid rgba(100, 180, 255, 0.08);
            text-decoration: none;
            transition: all 0.2s;
        }
        .nav-link:hover {
            color: #f1f5f9;
            background: rgba(100, 180, 255, 0.1);
            border-color: rgba(100, 180, 255, 0.2);
        }
        .nav-link.active {
            color: #3b82f6;
            background: rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
        }

        /* 准实时数据指示器 */
        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: #34d399;
        }
        .live-dot {
            width: 8px;
            height: 8px;
            background: #34d399;
            border-radius: 50%;
            animation: dashpulse 2s infinite;
        }
        @keyframes dashpulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }

        /* 状态标签（通用） */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge-green {
            background: rgba(34, 197, 94, 0.15);
            color: #34d399;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .badge-yellow {
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-red {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        /* 告警项卡片 */
        .alert-item {
            background: rgba(15,23,42,0.8);
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 10px;
            border-left: 3px solid #3b82f6;
        }
        .alert-item.critical { border-left-color: #ef4444; }
        .alert-item.warning { border-left-color: #f59e0b; }
        .alert-item.info { border-left-color: #3b82f6; }

        /* KPI 卡片（下钻用） */
        .kpi-card {
            background: linear-gradient(145deg, rgba(15,38,66,0.9) 0%, rgba(10,22,40,0.95) 100%);
            border: 1px solid rgba(100,180,255,0.08);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        .kpi-label {
            font-size: 11px;
            color: #cbd5e1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            color: #f1f5f9;
            margin: 8px 0;
            font-family: 'Inter', sans-serif;
        }
        .kpi-delta {
            font-size: 12px;
            font-weight: 600;
            color: #94a3b8;
        }
        .kpi-delta.up { color: #34d399; }
        .kpi-delta.down { color: #f87171; }

        /* 洞察 / 说明卡片 */
        .insight-card {
            background: linear-gradient(145deg, rgba(59,130,246,0.05) 0%, rgba(8,18,34,0.3) 100%);
            border: 1px solid rgba(59,130,246,0.1);
            border-left: 3px solid #3b82f6;
            border-radius: 0 10px 10px 0;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        .insight-card.warning {
            background: linear-gradient(145deg, rgba(245,158,11,0.05) 0%, rgba(8,18,34,0.3) 100%);
            border-color: rgba(245,158,11,0.15);
            border-left-color: #f59e0b;
        }
        .insight-card.danger {
            background: linear-gradient(145deg, rgba(239,68,68,0.05) 0%, rgba(8,18,34,0.3) 100%);
            border-color: rgba(239,68,68,0.15);
            border-left-color: #ef4444;
        }
        .insight-title {
            font-size: 13px;
            font-weight: 700;
            color: #e2e8f0;
            margin-bottom: 4px;
        }
        .insight-text {
            font-size: 12px;
            color: #cbd5e1;
            line-height: 1.45;
        }

        /* 隐藏默认元素 */
        footer { display: none !important; }
        header { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # 顶栏导航链接（与侧边栏保持一致）
    nav_items = [
        ("监控总览", "app"),
        ("监控中心", "monitor"),
        ("告警管理", "alert"),
        ("API文档", "api_docs"),
    ]
    nav_html = ""
    for name, page in nav_items:
        active_class = "active" if name == current_page else ""
        nav_html += f'<a href="/{page}" class="nav-link {active_class}">{name}</a>'

    st.markdown(f"""
    <div class="top-header">
        <div>
            <div class="top-header-title">企业数据智能监控大屏</div>
            <div class="top-header-subtitle">全链路业务数据准实时监控 | 智能预警 | 多维度分析</div>
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <div class="live-indicator">
                <div class="live-dot"></div>
                <span>准实时数据</span>
            </div>
            <div class="top-header-nav">
                {nav_html}
            </div>
            <div style="font-size:11px; color:#cbd5e1;">{current_time}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def resolve_query_date(selected_period):
    """根据时间范围选项，返回查询日期与对比日期"""
    now = datetime.now()
    if selected_period == "今日":
        query_date = now.strftime("%Y-%m-%d")
        compare_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    elif selected_period == "昨日":
        query_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        compare_date = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    elif selected_period == "本周":
        start = now - timedelta(days=now.weekday())
        query_date = start.strftime("%Y-%m-%d")
        compare_date = (start - timedelta(days=7)).strftime("%Y-%m-%d")
    elif selected_period == "本月":
        query_date = now.strftime("%Y-%m-01")
        compare_date = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-01")
    else:  # 自定义日期
        query_date = now.strftime("%Y-%m-%d")
        compare_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    return query_date, compare_date


def render_sidebar():
    """渲染统一的侧边栏控制面板（页面导航 + 时间筛选 + 自动刷新）"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="font-size:18px; font-weight:700; color:#e2e8f0;">企业数据监控大屏</div>
            <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">v2.0 | Flask + SQLite + Streamlit</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 页面导航
        st.markdown("<div style='font-size:12px; color:#e2e8f0; margin-bottom:8px; font-weight:600;'>页面导航</div>", unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            if st.button("监控总览", use_container_width=True, key="nav_home"):
                st.switch_page("app.py")
        with cols[1]:
            if st.button("监控中心", use_container_width=True, key="nav_monitor"):
                st.switch_page("pages/monitor.py")

        cols2 = st.columns(2)
        with cols2[0]:
            if st.button("告警管理", use_container_width=True, key="nav_alert"):
                st.switch_page("pages/alert.py")
        with cols2[1]:
            if st.button("API文档", use_container_width=True, key="nav_api"):
                st.switch_page("pages/api_docs.py")

        st.markdown("---")

        # 时间范围筛选
        st.markdown("<div style='font-size:12px; color:#e2e8f0; margin-bottom:8px; font-weight:600;'>时间范围</div>", unsafe_allow_html=True)
        selected_period = st.selectbox(
            "选择时间范围",
            ["今日", "昨日", "本周", "本月", "自定义日期"],
            index=0, key="time_filter", label_visibility="collapsed"
        )
        if selected_period == "自定义日期":
            custom_date = st.date_input("选择日期", datetime.now(), label_visibility="collapsed")
            selected_period = custom_date.strftime("%Y-%m-%d")

        st.markdown("---")

        # 自动刷新控制
        st.markdown("<div style='font-size:12px; color:#e2e8f0; margin-bottom:8px; font-weight:600;'>自动刷新</div>", unsafe_allow_html=True)

        auto_refresh = st.toggle("自动刷新数据", value=False, key="auto_refresh")
        refresh_interval = st.select_slider("刷新间隔", options=["2s", "5s", "10s", "30s"], value="5s", key="refresh_interval")

        if st.button("立即刷新", use_container_width=True, key="refresh_now"):
            st.rerun()

        st.markdown("---")

        # 数据源信息
        st.markdown("""
        <div style="font-size:11px; color:#cbd5e1; text-align:center; margin-top:20px;">
            <div>数据来源: 91天自洽业务数据</div>
            <div>后端: Flask RESTful API</div>
            <div style="margin-top:8px; color:#e2e8f0;">2026 企业数据监控大屏</div>
        </div>
        """, unsafe_allow_html=True)

        return auto_refresh, refresh_interval, selected_period


def render_live_badge():
    """渲染准实时数据角标"""
    st.markdown("""
    <div class="live-indicator" style="margin-bottom:12px;">
        <div class="live-dot"></div>
        <span>准实时数据流</span>
    </div>
    """, unsafe_allow_html=True)
