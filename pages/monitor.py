# 监控中心
"""
企业数据智能监控大屏 - 监控中心页
深色科技风 · 多维度数据监控
"""
import streamlit as st
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_generator import (
    generate_trend_data, generate_channel_data, generate_top_products,
    generate_kpi_data, generate_order_stream
)
from utils.navbar import render_navbar, render_sidebar, resolve_query_date

# ========== 统一导航栏 ==========
render_navbar("监控中心")
auto_refresh, refresh_interval, selected_period = render_sidebar()

query_date, _ = resolve_query_date(selected_period)

# 动态数据
if auto_refresh:
    import random
    random.seed(int(time.time() / 10))

# ========== KPI 概览 ==========
kpi = generate_kpi_data(query_date)
kpi_items = [
    ("销售额", kpi["sales"]["value"], kpi["sales"]["unit"], kpi["sales"]["change"], kpi["sales"]["trend"]),
    ("订单量", kpi["orders"]["value"], kpi["orders"]["unit"], kpi["orders"]["change"], kpi["orders"]["trend"]),
    ("在线用户", kpi["users"]["value"], kpi["users"]["unit"], kpi["users"]["change"], kpi["users"]["trend"]),
    ("转化率", kpi["conversion"]["value"], kpi["conversion"]["unit"], kpi["conversion"]["change"], kpi["conversion"]["trend"]),
    ("客单价", kpi["avg_order"]["value"], kpi["avg_order"]["unit"], kpi["avg_order"]["change"], kpi["avg_order"]["trend"]),
    ("复购用户", kpi["repeat"]["value"], kpi["repeat"]["unit"], kpi["repeat"]["change"], kpi["repeat"]["trend"]),
]

with st.container(border=True):
    st.markdown('<div class="panel-header">准实时经营概览</div>', unsafe_allow_html=True)
    kpi_cols = st.columns(6)
    for col, (name, val, unit, change, trend) in zip(kpi_cols, kpi_items):
        with col:
            arrow = "▲" if trend == "up" else ("▼" if trend == "down" else "─")
            css = "up" if trend == "up" else ("down" if trend == "down" else "flat")
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{name}</div>
                <div class="stat-value">{val}<span style="font-size:13px; color:#cbd5e1; margin-left:2px;">{unit}</span></div>
                <div class="stat-change {css}">{arrow} {change:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

# ========== 主区域：趋势 + 分布 ==========
with st.container(border=True):
    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown('<div class="panel-header">分时运营趋势</div>', unsafe_allow_html=True)

        trend_df = generate_trend_data(24, query_date)

        tab1, tab2, tab3 = st.tabs(["销售额", "订单量", "在线用户"])

        chart_configs = [
            ("销售额", "#3b82f6", "rgba(59,130,246,0.15)", "万"),
            ("订单量", "#8b5cf6", "rgba(139,92,246,0.15)", "单"),
            ("在线用户", "#ec4899", "rgba(236,72,153,0.15)", "人"),
        ]

        for tab, (col_name, color, fill_color, unit) in zip([tab1, tab2, tab3], chart_configs):
            with tab:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend_df["时间"], y=trend_df[col_name],
                    mode="lines+markers", line=dict(color=color, width=2.5),
                    fill="tozeroy", fillcolor=fill_color,
                    marker=dict(size=5, color=color),
                    hovertemplate=f"<b>%{{x}}</b><br>{col_name}: %{{y}}{unit}<extra></extra>",
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=10, b=30), height=280,
                    xaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=10), tickangle=45, nticks=12),
                    yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.5)", tickfont=dict(color="#cbd5e1", size=10)),
                    showlegend=False, hovermode="x unified",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown('<div class="panel-header">渠道占比</div>', unsafe_allow_html=True)

        ch_df = generate_channel_data(query_date)
        fig_ch = go.Figure(data=[go.Pie(
            labels=ch_df["渠道"], values=ch_df["订单量"], hole=0.65,
            textinfo="label+percent", textfont=dict(size=11, color="#e2e8f0"),
            marker=dict(colors=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"], line=dict(color="#1e293b", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value} 单<br>%{percent}<extra></extra>",
        )])
        fig_ch.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=10), height=300, showlegend=False,
            annotations=[dict(text=f"<b>{ch_df['订单量'].sum()}</b><br><span style='font-size:11px;color:#cbd5e1'>总订单</span>",
                               x=0.5, y=0.5, font_size=20, font_color="#e2e8f0", showarrow=False)],
        )
        st.plotly_chart(fig_ch, use_container_width=True, config={"displayModeBar": False})

        for _, r in ch_df.iterrows():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:6px 0; border-bottom:1px solid rgba(51,65,85,0.3);">
                <span style="font-size:11px; color:#cbd5e1;">{r['渠道']}</span>
                <span style="font-size:11px; font-weight:600; color:#e2e8f0;">{r['订单量']:,} <span style="color:#cbd5e1;">({r['占比']}%)</span></span>
            </div>
            """, unsafe_allow_html=True)

# ========== 第二行：热销商品 + 用户分布 + 订单流 ==========
with st.container(border=True):
    st.markdown('<div class="panel-header">商品与用户洞察</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        st.markdown('<div style="font-size:13px; color:#cbd5e1; margin-bottom:8px;">热销商品 TOP10</div>', unsafe_allow_html=True)

        top_df = generate_top_products(query_date)

        fig_top = go.Figure()
        colors_top = ["#f59e0b" if i == 0 else "#3b82f6" for i in range(len(top_df))]
        fig_top.add_trace(go.Bar(
            y=list(reversed(top_df["商品名称"])), x=list(reversed(top_df["销量"])),
            orientation="h",
            marker=dict(color=list(reversed(colors_top)), line=dict(color="#1e293b", width=0.5)),
            text=[f"{v}件" for v in reversed(top_df["销量"])],
            textposition="outside", textfont=dict(color="#cbd5e1", size=10),
            hovertemplate="<b>%{y}</b><br>销量: %{x}<br>环比: %{customdata}<extra></extra>",
            customdata=list(reversed([f"{v:+.1f}%" for v in top_df["环比(%)"]])) if "环比(%)" in top_df.columns else None,
        ))
        fig_top.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=130, r=40, t=10, b=10), height=340,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=10)),
            bargap=0.3,
        )
        st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown('<div style="font-size:13px; color:#cbd5e1; margin-bottom:8px;">用户地域分布</div>', unsafe_allow_html=True)

        provinces = ["广东", "浙江", "江苏", "北京", "上海", "四川", "山东", "福建", "湖北", "河南"]
        values = [2850, 1920, 1780, 1540, 1460, 1120, 1080, 950, 870, 820]
        colors_map = ["#1e3a5f", "#1e40af", "#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#dbeafe", "#eff6ff"]

        fig_map = go.Figure()
        fig_map.add_trace(go.Bar(
            y=list(reversed(provinces)), x=list(reversed(values)), orientation="h",
            marker=dict(color=list(reversed(colors_map)), line=dict(color="#1e293b", width=0.5)),
            text=[f"{v}" for v in reversed(values)], textposition="outside",
            textfont=dict(color="#cbd5e1", size=10),
            hovertemplate="<b>%{y}</b><br>活跃用户: %{x}<extra></extra>",
        ))
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=50, r=30, t=10, b=10), height=340,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=11)),
            bargap=0.25,
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

    with c3:
        st.markdown('<div style="font-size:13px; color:#cbd5e1; margin-bottom:8px;">准实时订单流水</div>', unsafe_allow_html=True)

        order_df = generate_order_stream(12)

        table_html = """
        <table style="width:100%; border-collapse:collapse; font-size:10px;">
            <thead>
                <tr style="background:#1e293b;">
                    <th style="padding:6px 8px; text-align:left; color:#cbd5e1; border-bottom:1px solid #334155;">订单</th>
                    <th style="padding:6px 8px; text-align:center; color:#cbd5e1; border-bottom:1px solid #334155;">金额</th>
                    <th style="padding:6px 8px; text-align:center; color:#cbd5e1; border-bottom:1px solid #334155;">状态</th>
                </tr>
            </thead>
            <tbody>
        """
        status_colors = {
            "已完成": ("#064e3b", "#10b981"), "配送中": ("#713f12", "#f59e0b"),
            "待发货": ("#1e3a5f", "#3b82f6"), "已取消": ("#7f1d1d", "#ef4444"),
        }
        for _, row in order_df.iterrows():
            oid = str(row["订单编号"])[-10:]
            bg, color = status_colors.get(row["订单状态"], ("#1e293b", "#cbd5e1"))
            table_html += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="padding:6px 8px; color:#cbd5e1; font-family:monospace;">{oid}</td>
                <td style="padding:6px 8px; color:#e2e8f0; text-align:center; font-weight:600;">{row['消费金额']}</td>
                <td style="padding:6px 8px; text-align:center;">
                    <span style="background:{bg}; color:{color}; padding:1px 6px; border-radius:3px; font-size:9px; font-weight:600;">{row['订单状态']}</span>
                </td>
            </tr>
            """
        table_html += "</tbody></table>"
        st.html(table_html)

# 底部
st.markdown(f"""
<div style="text-align:center; padding:12px; color:#cbd5e1; font-size:11px; border-top:1px solid rgba(100,180,255,0.1); margin-top:12px;">
    企业数据监控大屏 · 数据日期: {query_date} · 刷新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# 自动刷新
if auto_refresh:
    interval_seconds = int(refresh_interval.replace("s", ""))
    time.sleep(interval_seconds)
    st.rerun()
