import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_generator import (
    generate_kpi_data, generate_trend_data, generate_channel_data,
    generate_top_products, generate_alert_data, generate_order_stream
)
from datetime import datetime

st.set_page_config(page_title="企业数据监控大屏", page_icon="", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #0f172a 50%, #1e1b4b 100%);
    }
    header { visibility: hidden; }
    .stDeployButton { display: none; }
    footer { visibility: hidden; }
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
    }
    [data-testid="stSidebar"] { display: none; }
    .stButton > button {
        background: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        padding: 4px 14px !important;
    }
    .stButton > button:hover {
        background: #334155 !important;
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; 
            background: rgba(15, 23, 42, 0.9); border: 1px solid #334155; border-radius: 12px;
            padding: 14px 24px; margin-bottom: 16px; backdrop-filter: blur(10px);">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div>
            <div style="font-size: 22px; font-weight: 800; color: #e2e8f0; letter-spacing: 1px;">
                企业数据监控大屏
            </div>
            <div style="font-size: 11px; color: #64748b; letter-spacing: 2px; margin-top: 2px;">
                ENTERPRISE DATA MONITORING DASHBOARD
            </div>
        </div>
        <div style="width: 2px; height: 32px; background: #3b82f6; border-radius: 1px;"></div>
    </div>
    <div style="text-align: center;">
        <div style="font-size: 24px; font-weight: 700; color: #e2e8f0; font-family: 'Courier New', monospace;">
            {current_time}
        </div>
        <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
            数据每 5 秒自动刷新
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 4px 12px;">
            <span style="color: #64748b; font-size: 11px;">今日</span>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 4px 12px;">
            <span style="color: #64748b; font-size: 11px;">全渠道</span>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 6px 14px;">
            <span style="color: #3b82f6; font-size: 12px; font-weight: 600;">刷新</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

kpi_data = generate_kpi_data()

kpi_items = [
    ("实时销售额", kpi_data["sales"]["value"], kpi_data["sales"]["unit"], kpi_data["sales"]["change"], kpi_data["sales"]["trend"], "#3b82f6"),
    ("实时订单量", kpi_data["orders"]["value"], kpi_data["orders"]["unit"], kpi_data["orders"]["change"], kpi_data["orders"]["trend"], "#8b5cf6"),
    ("在线用户数", kpi_data["users"]["value"], kpi_data["users"]["unit"], kpi_data["users"]["change"], kpi_data["users"]["trend"], "#ec4899"),
    ("整体转化率", kpi_data["conversion"]["value"], kpi_data["conversion"]["unit"], kpi_data["conversion"]["change"], kpi_data["conversion"]["trend"], "#10b981"),
    ("客单价", kpi_data["avg_order"]["value"], kpi_data["avg_order"]["unit"], kpi_data["avg_order"]["change"], kpi_data["avg_order"]["trend"], "#f59e0b"),
    ("复购用户", kpi_data["repeat"]["value"], kpi_data["repeat"]["unit"], kpi_data["repeat"]["change"], kpi_data["repeat"]["trend"], "#06b6d4"),
]

kpi_html = '<div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; margin-bottom: 16px;">'

for title, value, unit, change, trend, color in kpi_items:
    if trend == "up":
        arrow = "&#9650;"
        change_color = "#10b981"
        change_bg = "rgba(16, 185, 129, 0.1)"
    elif trend == "down":
        arrow = "&#9660;"
        change_color = "#ef4444"
        change_bg = "rgba(239, 68, 68, 0.1)"
    else:
        arrow = "&#9472;"
        change_color = "#64748b"
        change_bg = "rgba(100, 116, 139, 0.1)"

    change_text = f"{change:+.1f}%" if change != 0 else "持平"

    kpi_html += f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
                border: 1px solid {color}33; border-radius: 12px; padding: 18px 16px;
                position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: {color}; border-radius: 12px 12px 0 0;"></div>
        <div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px; font-weight: 500;">{title}</div>
        <div style="display: flex; align-items: baseline; gap: 4px; margin-bottom: 8px;">
            <span style="font-size: 26px; font-weight: 800; color: #e2e8f0;">{value}</span>
            <span style="font-size: 13px; color: #64748b;">{unit}</span>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 4px; 
                    background: {change_bg}; padding: 3px 10px; border-radius: 20px;">
            <span style="color: {change_color}; font-size: 12px; font-weight: 600;">{arrow} {change_text}</span>
        </div>
    </div>
    """

kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
    <div style="width: 4px; height: 18px; background: #3b82f6; border-radius: 2px;"></div>
    <span style="font-size: 15px; font-weight: 700; color: #e2e8f0;">核心指标分时趋势</span>
    <div style="flex: 1; height: 1px; background: #334155;"></div>
</div>
""", unsafe_allow_html=True)

trend_df = generate_trend_data(24)

col1, col2, col3 = st.columns(3)

chart_configs = [
    (col1, "销售额分时趋势", "销售额", "#3b82f6", "rgba(59, 130, 246, 0.15)"),
    (col2, "订单量分时趋势", "订单量", "#8b5cf6", "rgba(139, 92, 246, 0.15)"),
    (col3, "在线用户分时趋势", "在线用户", "#ec4899", "rgba(236, 72, 153, 0.15)"),
]

for i, (col, title, col_name, color, fill_color) in enumerate(chart_configs):
    with col:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 12px; padding: 14px;">
            <div style="font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 10px;">{title}</div>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_df["时间"],
            y=trend_df[col_name],
            mode="lines",
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate=f"<b>%{{x}}</b><br>{col_name}: %{{y}}<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=30),
            height=220,
            xaxis=dict(
                showgrid=False,
                tickfont=dict(color="#64748b", size=10),
                tickangle=45,
                nticks=8,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(51, 65, 85, 0.5)",
                tickfont=dict(color="#64748b", size=10),
                zeroline=False,
            ),
            showlegend=False,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True, key=f"trend_{i}")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin: 16px 0 12px 0;">
    <div style="width: 4px; height: 18px; background: #8b5cf6; border-radius: 2px;"></div>
    <span style="font-size: 15px; font-weight: 700; color: #e2e8f0;">维度拆解分析</span>
    <div style="flex: 1; height: 1px; background: #334155;"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 12px; padding: 14px;">
        <div style="font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 10px;">全国用户分布热力图</div>
    """, unsafe_allow_html=True)

    map_provinces = ["广东", "浙江", "江苏", "北京", "上海", "四川", "山东", "福建", "湖北", "河南"]
    map_values = [2850, 1920, 1780, 1540, 1460, 1120, 1080, 950, 870, 820]
    map_colors = ["#1e3a5f", "#1e40af", "#1d4ed8", "#2563eb", "#3b82f6", 
                  "#60a5fa", "#93c5fd", "#bfdbfe", "#dbeafe", "#eff6ff"]

    fig_map = go.Figure()
    fig_map.add_trace(go.Bar(
        y=list(reversed(map_provinces)),
        x=list(reversed(map_values)),
        orientation="h",
        marker=dict(
            color=list(reversed(map_colors)),
            line=dict(color="#1e293b", width=1),
        ),
        text=[f"{v}" for v in reversed(map_values)],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
        hovertemplate="<b>%{y}</b><br>活跃用户: %{x}<extra></extra>",
    ))
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=40, t=10, b=10),
        height=280,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=12)),
        bargap=0.25,
    )
    st.plotly_chart(fig_map, use_container_width=True, key="map_chart_main")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 12px; padding: 14px;">
        <div style="font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 10px;">渠道订单占比</div>
    """, unsafe_allow_html=True)

    channel_df = generate_channel_data()
    fig_channel = go.Figure(data=[go.Pie(
        labels=channel_df["渠道"],
        values=channel_df["订单量"],
        hole=0.6,
        textinfo="label+percent",
        textfont=dict(size=11, color="#e2e8f0"),
        marker=dict(
            colors=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"],
            line=dict(color="#1e293b", width=2),
        ),
        hovertemplate="<b>%{label}</b><br>订单量: %{value}<br>占比: %{percent}<extra></extra>",
    )])
    fig_channel.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=10),
        height=280,
        showlegend=False,
        annotations=[dict(
            text=f"<b>{channel_df['订单量'].sum()}</b><br><span style='font-size:11px;color:#94a3b8'>总订单</span>",
            x=0.5, y=0.5,
            font_size=18,
            font_color="#e2e8f0",
            showarrow=False,
        )],
    )
    st.plotly_chart(fig_channel, use_container_width=True, key="channel_chart_main")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 12px; padding: 14px;">
        <div style="font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 10px;">热销商品 TOP10</div>
    """, unsafe_allow_html=True)

    top_df = generate_top_products()

    fig_top = go.Figure()
    colors_top = ["#f59e0b" if i == 0 else "#3b82f6" for i in range(len(top_df))]
    fig_top.add_trace(go.Bar(
        y=list(reversed(top_df["商品名称"].tolist())),
        x=list(reversed(top_df["销量"].tolist())),
        orientation="h",
        marker=dict(
            color=list(reversed(colors_top)),
            line=dict(color="#1e293b", width=1),
        ),
        text=[f"{v}" for v in reversed(top_df["销量"].tolist())],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=10),
        hovertemplate="<b>%{y}</b><br>销量: %{x}<extra></extra>",
    ))
    fig_top.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=120, r=30, t=10, b=10),
        height=280,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=10)),
        bargap=0.3,
    )
    st.plotly_chart(fig_top, use_container_width=True, key="top_chart_main")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin: 16px 0 12px 0;">
    <div style="width: 4px; height: 18px; background: #ef4444; border-radius: 2px;"></div>
    <span style="font-size: 15px; font-weight: 700; color: #e2e8f0;">实时监控与告警</span>
    <div style="flex: 1; height: 1px; background: #334155;"></div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 12px; padding: 14px;">
        <div style="font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 12px;">告警监控</div>
    """, unsafe_allow_html=True)

    alert_stats = [
        ("高危告警", "1", "#ef4444", "#7f1d1d"),
        ("中危告警", "2", "#f59e0b", "#713f12"),
        ("低危告警", "2", "#3b82f6", "#1e3a5f"),
    ]

    stats_html = '<div style="display: flex; gap: 10px; margin-bottom: 14px;">'
    for name, count, color, bg in alert_stats:
        stats_html += f"""
        <div style="flex: 1; background: {bg}; border: 1px solid {color}44; border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 20px; font-weight: 800; color: {color};">{count}</div>
            <div style="font-size: 11px; color: {color}aa; margin-top: 2px;">{name}</div>
        </div>
        """
    stats_html += '</div>'
    st.markdown(stats_html, unsafe_allow_html=True)

    alert_df = generate_alert_data()
    for _, row in alert_df.head(4).iterrows():
        level_color = {"高危": "#ef4444", "中危": "#f59e0b", "低危": "#3b82f6"}[row["level"]]
        level_bg = {"高危": "#7f1d1d", "中危": "#713f12", "低危": "#1e3a5f"}[row["level"]]
        status_color = {"未处理": "#ef4444", "处理中": "#f59e0b", "已处理": "#10b981"}[row["status"]]

        st.markdown(f"""
        <div style="background: #0f172a; border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; 
                    border-left: 3px solid {level_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: {level_bg}; color: {level_color}; padding: 1px 8px; border-radius: 3px; font-size: 10px; font-weight: 600;">{row["level"]}</span>
                    <span style="color: #e2e8f0; font-weight: 600; font-size: 12px;">{row["type"]}</span>
                </div>
                <span style="color: #64748b; font-size: 10px;">{row["time"]}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #94a3b8; font-size: 11px;">{row["value"]}</span>
                <span style="background: {'#7f1d1d' if row['status']=='未处理' else '#713f12' if row['status']=='处理中' else '#064e3b'}; 
                             color: {status_color}; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600;">{row["status"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 12px; padding: 14px;">
        <div style="font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 12px;">实时订单流水</div>
    """, unsafe_allow_html=True)

    order_df = generate_order_stream()

    table_html = """
    <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
        <thead>
            <tr style="background: #1e293b;">
                <th style="padding: 8px 10px; text-align: left; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #334155;">订单编号</th>
                <th style="padding: 8px 10px; text-align: left; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #334155;">时间</th>
                <th style="padding: 8px 10px; text-align: right; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #334155;">金额</th>
                <th style="padding: 8px 10px; text-align: center; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #334155;">状态</th>
            </tr>
        </thead>
        <tbody>
    """

    status_colors = {
        "已完成": ("#064e3b", "#10b981"),
        "配送中": ("#713f12", "#f59e0b"),
        "待发货": ("#1e3a5f", "#3b82f6"),
        "已取消": ("#7f1d1d", "#ef4444"),
    }

    for _, row in order_df.iterrows():
        bg, color = status_colors.get(row["订单状态"], ("#1e293b", "#94a3b8"))
        table_html += f"""
        <tr style="border-bottom: 1px solid #1e293b;">
            <td style="padding: 8px 10px; color: #cbd5e1; font-family: monospace; font-size: 11px;">{row["订单编号"][-8:]}</td>
            <td style="padding: 8px 10px; color: #94a3b8; font-size: 11px;">{row["下单时间"]}</td>
            <td style="padding: 8px 10px; color: #e2e8f0; text-align: right; font-weight: 600;">{row["消费金额"]}</td>
            <td style="padding: 8px 10px; text-align: center;">
                <span style="background: {bg}; color: {color}; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600;">{row["订单状态"]}</span>
            </td>
        </tr>
        """

    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
export_col1, export_col2, export_col3 = st.columns([1, 1, 4])
with export_col1:
    if st.button("导出报表", key="export_btn"):
        st.toast("报表导出成功！", icon="")
with export_col2:
    if st.button("全屏展示", key="fullscreen_btn"):
        st.toast("按 F11 进入全屏模式", icon="")
