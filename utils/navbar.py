"""
企业数据监控大屏 - 共享导航栏组件
统一页面标题 + 顶部导航栏 + 动态刷新
"""
import streamlit as st
import time
from datetime import datetime

def render_dashboard_header(current_page="监控总览"):
    """
    渲染统一的顶部标题栏和导航
    """
    # 统一的页面标题（所有子页面保持一致）
    st.set_page_config(
        page_title="企业数据监控大屏",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 隐藏侧边栏和默认导航
    st.markdown("""
    <style>
        /* 隐藏 Streamlit 默认导航 */
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        
        /* 全局背景 */
        .stApp { background: linear-gradient(135deg, #0b1120 0%, #0f172a 50%, #1e1b4b 100%); }
        
        /* 主内容区 */
        .block-container { 
            padding-top: 0.5rem !important; 
            padding-bottom: 0.5rem !important; 
            max-width: 100% !important; 
        }
        
        /* 顶部标题栏 */
        .dashboard-header {
            background: linear-gradient(90deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.95) 100%);
            border: 1px solid rgba(59,130,246,0.1);
            border-radius: 12px;
            padding: 14px 24px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .dashboard-header-title {
            font-size: 20px;
            font-weight: 800;
            color: #f1f5f9;
        }
        .dashboard-header-subtitle {
            font-size: 11px;
            color: #64748b;
        }
        .dashboard-header-nav {
            display: flex;
            gap: 8px;
        }
        .dash-nav-link {
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            color: #94a3b8;
            background: rgba(59,130,246,0.05);
            border: 1px solid rgba(59,130,246,0.08);
            text-decoration: none;
            transition: all 0.2s;
        }
        .dash-nav-link:hover {
            color: #e2e8f0;
            background: rgba(59,130,246,0.1);
            border-color: rgba(59,130,246,0.2);
        }
        .dash-nav-link.active {
            color: #3b82f6;
            background: rgba(59,130,246,0.12);
            border-color: rgba(59,130,246,0.3);
        }
        
        /* 实时数据指示器 */
        @keyframes dash-pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.15); }
        }
        .dash-live-dot {
            width: 8px; height: 8px; background: #34d399; border-radius: 50%;
            animation: dash-pulse 2s infinite; display: inline-block;
        }
        .dash-live-text {
            font-size: 12px; color: #34d399; margin-left: 6px;
        }
        
        /* 通用面板 */
        .panel-card {
            background: linear-gradient(145deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.95) 100%);
            border: 1px solid rgba(59,130,246,0.06);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }
        .panel-header {
            display: flex; align-items: center; gap: 8px;
            font-size: 14px; font-weight: 700; color: #e2e8f0; margin-bottom: 14px;
        }
        .panel-header::before {
            content: ''; width: 4px; height: 18px; background: #3b82f6; border-radius: 2px;
        }
        
        /* 统计卡片 */
        .stat-card {
            background: linear-gradient(145deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.95) 100%);
            border: 1px solid rgba(59,130,246,0.1); border-radius: 12px; padding: 16px;
            text-align: center; position: relative; overflow: hidden;
        }
        .stat-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #3b82f6, #06b6d4); border-radius: 12px 12px 0 0;
        }
        .stat-value { font-size: 28px; font-weight: 800; color: #f1f5f9; font-family: 'Inter', sans-serif; }
        .stat-label { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
        .stat-change { font-size: 12px; font-weight: 600; margin-top: 4px; }
        .stat-change.up { color: #10b981; }
        .stat-change.down { color: #ef4444; }
        
        /* 按钮 */
        .stButton > button { background: #1e293b !important; color: #94a3b8 !important; border: 1px solid #334155 !important; border-radius: 6px !important; font-size: 12px !important; cursor: pointer !important; }
        .stButton > button:hover { background: #334155 !important; color: #e2e8f0 !important; border-color: #3b82f6 !important; }
        .stSelectbox > div > div { background: #1e293b !important; border: 1px solid #334155 !important; border-radius: 6px !important; }
        .stSelectbox label { color: #94a3b8 !important; font-size: 12px !important; }
        
        footer { display: none !important; }
        header { visibility: hidden; }
        .stDeployButton { display: none; }
    </style>
    """, unsafe_allow_html=True)
    
    # 导航链接
    nav_items = [
        ("监控总览", ""),
        ("实时监控", "monitor"),
        ("告警管理", "alert"),
    ]
    
    nav_html = ""
    for name, page in nav_items:
        active_class = "active" if name == current_page else ""
        href = page if page else "app"
        nav_html += f'<a href="/{href}" target="_self" class="dash-nav-link {active_class}">{name}</a>'
    
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # 渲染顶部标题栏
    st.markdown(f"""
    <div class="dashboard-header">
        <div>
            <div class="dashboard-header-title">企业数据智能监控大屏</div>
            <div class="dashboard-header-subtitle">全链路业务数据实时监控 | 智能预警 | 多维度分析</div>
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="display:flex; align-items:center;">
                <div class="dash-live-dot"></div>
                <span class="dash-live-text">实时数据</span>
            </div>
            <div class="dashboard-header-nav">
                {nav_html}
            </div>
            <div style="font-size:11px; color:#475569;">{current_time}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_refresh_controls():
    """
    渲染时间筛选器和刷新按钮（在标题栏下方）
    """
    time_options = ["今日", "昨日", "本周", "本月", "自定义日期"]
    
    col1, col2, col3, col4 = st.columns([1, 1, 0.5, 0.5])
    
    with col1:
        selected_period = st.selectbox("", time_options, key="time_filter", label_visibility="collapsed")
    
    with col3:
        auto_refresh = st.toggle("", False, key="auto_refresh_toggle", label_visibility="collapsed")
    
    with col4:
        if st.button("刷新", use_container_width=True, key="refresh_btn"):
            st.rerun()
    
    return selected_period, auto_refresh
