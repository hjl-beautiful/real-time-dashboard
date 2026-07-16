"""
企业数据监控大屏 - 告警管理页
"""
import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_generator import generate_alert_data
from utils.navbar import render_dashboard_header, render_refresh_controls

# ========== 统一导航栏 ==========
render_dashboard_header("告警管理")
selected_period, auto_refresh = render_refresh_controls()

now = datetime.now()
query_date = now.strftime("%Y-%m-%d")

# 动态数据
if auto_refresh:
    seed = int(time.time() / 10)
    random.seed(seed)

alert_df = generate_alert_data(query_date)

# ========== 告警概览 ==========
high_count = len(alert_df[alert_df["level"] == "高危"])
mid_count = len(alert_df[alert_df["level"] == "中危"])
low_count = len(alert_df[alert_df["level"] == "低危"])
unresolved = len(alert_df[alert_df["status"] == "未处理"])

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(f"""
    <div class="stat-card" style="border:1px solid #b91c1c;">
        <div class="stat-value" style="color:#fca5a5;">{high_count}</div>
        <div class="stat-label" style="color:#f87171;"> 高危告警</div>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown(f"""
    <div class="stat-card" style="border:1px solid #ca8a04;">
        <div class="stat-value" style="color:#fde047;">{mid_count}</div>
        <div class="stat-label" style="color:#facc15;"> 中危告警</div>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown(f"""
    <div class="stat-card" style="border:1px solid #3b82f6;">
        <div class="stat-value" style="color:#93c5fd;">{low_count}</div>
        <div class="stat-label" style="color:#60a5fa;"> 低危告警</div>
    </div>
    """, unsafe_allow_html=True)

with s4:
    st.markdown(f"""
    <div class="stat-card" style="border:1px solid #ef4444;">
        <div class="stat-value" style="color:#f87171;">{unresolved}</div>
        <div class="stat-label" style="color:#f87171;"> 待处理</div>
    </div>
    """, unsafe_allow_html=True)

# ========== 告警趋势模拟 ==========
st.markdown('<div class="panel-header" style="margin-top:20px;"> 近24小时告警趋势</div>', unsafe_allow_html=True)

hours = [(now - timedelta(hours=h)).strftime("%H:00") for h in range(23, -1, -1)]
high_trend = [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1]
mid_trend  = [1,0,1,0,0,1,0,1,0,0,0,0,1,1,0,0,1,0,1,0,0,1,1,2]
low_trend  = [0,1,1,0,0,1,0,0,1,2,0,0,1,0,1,1,0,0,0,1,0,0,1,2]

fig_trend = go.Figure()
fig_trend.add_trace(go.Bar(
    x=hours, y=high_trend, name="高危", marker_color="#ef4444",
    hovertemplate="<b>%{x}</b><br>高危: %{y}条<extra></extra>"
))
fig_trend.add_trace(go.Bar(
    x=hours, y=mid_trend, name="中危", marker_color="#f59e0b",
    hovertemplate="<b>%{x}</b><br>中危: %{y}条<extra></extra>"
))
fig_trend.add_trace(go.Bar(
    x=hours, y=low_trend, name="低危", marker_color="#3b82f6",
    hovertemplate="<b>%{x}</b><br>低危: %{y}条<extra></extra>"
))
fig_trend.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    barmode="stack", font=dict(color="#94a3b8"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                 font=dict(color="#94a3b8", size=11)),
    margin=dict(l=20, r=20, t=10, b=20), height=220,
    xaxis=dict(showgrid=False, tickfont=dict(color="#64748b", size=10), tickangle=45, nticks=12),
    yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.5)", tickfont=dict(color="#64748b"),
               title="告警数量", title_font_color="#64748b"),
)
st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

# ========== 告警列表 ==========
st.markdown('<div class="panel-header" style="margin-top:20px;"> 告警详情列表</div>', unsafe_allow_html=True)

col_alerts, col_detail = st.columns([3, 2])

with col_alerts:
    for _, row in alert_df.iterrows():
        level = row["level"]
        level_color = {"高危": "#ef4444", "中危": "#f59e0b", "低危": "#3b82f6"}[level]
        level_bg = {"高危": "#7f1d1d", "中危": "#713f12", "低危": "#1e3a5f"}[level]
        status_color = {"未处理": "#ef4444", "处理中": "#f59e0b", "已处理": "#10b981"}[row["status"]]
        status_bg = {"未处理": "#7f1d1d", "处理中": "#713f12", "已处理": "#064e3b"}[row["status"]]
        css_class = {"高危": "critical", "中危": "warning", "低危": "info"}[level]
        
        st.html(f"""
        <div class="alert-item {css_class}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="background:{level_bg}; color:{level_color}; padding:2px 10px; 
                                 border-radius:4px; font-size:10px; font-weight:700;">{level}</span>
                    <span style="color:#e2e8f0; font-weight:600; font-size:13px;">{row['type']}</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:#64748b; font-size:10px;">{row['time']}</span>
                    <span style="background:{status_bg}; color:{status_color}; padding:2px 8px; 
                                 border-radius:4px; font-size:10px; font-weight:600;">{row['status']}</span>
                </div>
            </div>
            <div style="color:#94a3b8; font-size:11px;">{row['value']}</div>
        </div>
        """)

with col_detail:
    # 告警统计
    st.markdown('<div class="panel-header" style="margin-top:0;"> 告警分布</div>', unsafe_allow_html=True)
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=["高危", "中危", "低危"], values=[high_count, mid_count, low_count],
        hole=0.65, textinfo="label+value",
        marker=dict(colors=["#ef4444", "#f59e0b", "#3b82f6"], line=dict(color="#1e293b", width=2)),
        textfont=dict(color="#e2e8f0", size=12),
    )])
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=10), height=240, showlegend=False,
        annotations=[dict(
            text=f"<b>{len(alert_df)}</b><br><span style='font-size:11px;color:#94a3b8'>总计</span>",
            x=0.5, y=0.5, font_size=22, font_color="#e2e8f0", showarrow=False
        )],
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
    
    # 处理建议
    st.markdown('<div class="panel-header" style="margin-top:16px;"> 处理建议</div>', unsafe_allow_html=True)
    
    suggestions = [
        (" 高危告警", "立即通知值班负责人，启动应急预案。确认影响范围，同步相关业务方。", "critical"),
        (" 中危告警", "30分钟内响应，排查根因。如持续恶化则升级处理。", "warning"),
        (" 低危告警", "记录并纳入日常巡检，趋势监控即可。", "info"),
    ]
    
    for title, desc, cls in suggestions:
        border = {"critical": "#ef4444", "warning": "#f59e0b", "info": "#3b82f6"}[cls]
        bg = {"critical": "rgba(239,68,68,0.05)", "warning": "rgba(245,158,11,0.05)", "info": "rgba(59,130,246,0.05)"}[cls]
        st.markdown(f"""
        <div style="background:{bg}; border-left:3px solid {border}; border-radius:0 8px 8px 0; 
                    padding:12px 14px; margin-bottom:8px;">
            <div style="font-size:12px; font-weight:700; color:#e2e8f0; margin-bottom:4px;">{title}</div>
            <div style="font-size:11px; color:#94a3b8; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# 底部
st.html(f"""
<div style="text-align:center; padding:12px; color:#475569; font-size:11px; border-top:1px solid #1e293b; margin-top:16px;">
    告警管理中心 · 监控 {len(alert_df)} 条告警 · {unresolved} 条待处理 · {now.strftime("%Y-%m-%d %H:%M:%S")}
</div>
""")

# 自动刷新
if auto_refresh:
    time.sleep(5)
    st.rerun()
