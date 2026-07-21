"""
企业数据智能监控大屏 - 监控总览页
KPI 指标卡 + 时间筛选 + 指标下钻 + 多维度分析
"""
import streamlit as st
import time
import plotly.graph_objects as go
import plotly.express as px
from utils.data_generator import (
    generate_kpi_data, generate_trend_data, generate_channel_data,
    generate_top_products, generate_alert_data, generate_order_stream,
    generate_province_distribution,
    get_kpi_detail, get_kpi_detail_by_dimension
)
from utils.navbar import render_navbar, render_sidebar, resolve_query_date
from datetime import datetime, timedelta

# ========== 统一导航栏 + 侧边栏 ==========
render_navbar("监控总览")
auto_refresh, refresh_interval, selected_period = render_sidebar()

# 初始化 session_state
if "selected_kpi" not in st.session_state:
    st.session_state.selected_kpi = None

now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

# 确定查询日期
query_date, compare_date = resolve_query_date(selected_period)

# ========== KPI 卡片（可点击下钻）==========
kpi_data = generate_kpi_data(query_date, compare_date)
kpi_items = [
    ("销售额(日)", kpi_data["sales"]["value"], kpi_data["sales"]["unit"], kpi_data["sales"]["change"], kpi_data["sales"]["trend"], "#3b82f6", "sales"),
    ("订单量(日)", kpi_data["orders"]["value"], kpi_data["orders"]["unit"], kpi_data["orders"]["change"], kpi_data["orders"]["trend"], "#8b5cf6", "orders"),
    ("客单价", kpi_data["avg_order"]["value"], kpi_data["avg_order"]["unit"], kpi_data["avg_order"]["change"], kpi_data["avg_order"]["trend"], "#f59e0b", "avg_order"),
    ("付款率", kpi_data["pay_rate"]["value"], kpi_data["pay_rate"]["unit"], kpi_data["pay_rate"]["change"], kpi_data["pay_rate"]["trend"], "#10b981", "pay_rate"),
    ("退款率", kpi_data["refund_rate"]["value"], kpi_data["refund_rate"]["unit"], kpi_data["refund_rate"]["change"], kpi_data["refund_rate"]["trend"], "#ef4444", "refund_rate"),
    ("覆盖省份", kpi_data["provinces"]["value"], kpi_data["provinces"]["unit"], kpi_data["provinces"]["change"], kpi_data["provinces"]["trend"], "#06b6d4", "provinces"),
]

with st.container(border=True):
    st.markdown(
        '<div class="panel-header" style="margin-bottom:10px;">核心经营指标 '
        '<span style="font-size:11px; color:#cbd5e1; font-weight:400; margin-left:6px;">点击卡片可下钻查看多维度明细</span></div>',
        unsafe_allow_html=True
    )

    kpi_cols = st.columns(6)
    for i, (title, value, unit, change, trend, color, key) in enumerate(kpi_items):
        with kpi_cols[i]:
            if trend == "up":
                arrow = "▲"; change_color = "#34d399"; change_bg = "rgba(16,185,129,0.1)"
            elif trend == "down":
                arrow = "▼"; change_color = "#f87171"; change_bg = "rgba(239,68,68,0.1)"
            else:
                arrow = "─"; change_color = "#cbd5e1"; change_bg = "rgba(100,116,139,0.1)"
            change_text = f"{change:+.1f}%" if change != 0 else "持平"

            kpi_html = f"""
            <div style="background:linear-gradient(135deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.95) 100%); border:1px solid {color}33; border-radius:12px; padding:14px 12px; position:relative; overflow:hidden; cursor:pointer;">
                <div style="position:absolute; top:0; left:0; right:0; height:3px; background:{color}; border-radius:12px 12px 0 0;"></div>
                <div style="font-size:12px; color:#cbd5e1; margin-bottom:6px; font-weight:500;">{title}</div>
                <div style="display:flex; align-items:baseline; gap:4px; margin-bottom:6px;">
                    <span style="font-size:26px; font-weight:800; color:#e2e8f0;">{value}</span>
                    <span style="font-size:13px; color:#cbd5e1;">{unit}</span>
                </div>
                <div style="display:inline-flex; align-items:center; gap:4px; background:{change_bg}; padding:3px 10px; border-radius:20px;">
                    <span style="color:{change_color}; font-size:12px; font-weight:600;">{arrow} {change_text}</span>
                </div>
                <div style="font-size:10px; color:#cbd5e1; margin-top:6px;">点击查看明细</div>
            </div>
            """
            st.html(kpi_html)

            # 点击下钻
            if st.button("查看明细", key=f"drill_{key}", use_container_width=True):
                st.session_state.selected_kpi = key

# ========== KPI 多维度下钻面板 ==========
if st.session_state.selected_kpi:
    kpi_name_map = {
        "sales": "销售额",
        "orders": "订单量",
        "avg_order": "客单价",
        "pay_rate": "付款率",
        "refund_rate": "退款率",
        "provinces": "覆盖省份",
    }
    drill_name = kpi_name_map.get(st.session_state.selected_kpi, st.session_state.selected_kpi)

    # 不同 KPI 支持的下钻维度
    dimension_options = {
        "sales": ["时间", "省份", "订单状态"],
        "orders": ["时间", "省份"],
        "avg_order": ["时间", "省份"],
        "pay_rate": ["时间", "省份"],
        "refund_rate": ["时间", "省份"],
        "provinces": ["时间"],
    }
    available_dims = dimension_options.get(st.session_state.selected_kpi, ["时间"])
    dim_key = f"drill_dim_{st.session_state.selected_kpi}"
    if dim_key not in st.session_state:
        st.session_state[dim_key] = available_dims[0]

    with st.container(border=True):
        st.markdown(
            f'<div class="panel-header">{drill_name} 下钻分析 '
            f'<span style="font-size:11px; color:#cbd5e1; font-weight:400; margin-left:6px;">({query_date})</span></div>',
            unsafe_allow_html=True
        )

        col_dim, col_close = st.columns([3, 1])
        with col_dim:
            selected_dim = st.selectbox(
                "选择下钻维度",
                available_dims,
                key=dim_key,
                label_visibility="collapsed"
            )
        with col_close:
            st.write("")
            st.write("")
            if st.button("关闭明细", key="close_drill", use_container_width=True):
                st.session_state.selected_kpi = None
                st.rerun()

        detail_df = get_kpi_detail_by_dimension(st.session_state.selected_kpi, selected_dim, query_date)
        if not detail_df.empty:
            x_col = detail_df.columns[0]
            y_col = detail_df.columns[1]

            fig_detail = go.Figure()
            fig_detail.add_trace(go.Bar(
                x=detail_df[x_col], y=detail_df[y_col],
                marker=dict(color="#3b82f6", line=dict(color="#1e293b", width=0.5)),
                hovertemplate=f"<b>%{{x}}</b><br>{drill_name}: %{{y}}<extra></extra>",
            ))
            fig_detail.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=30), height=240,
                xaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=10), tickangle=45),
                yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.5)", tickfont=dict(color="#cbd5e1", size=10)),
                showlegend=False,
            )
            st.plotly_chart(fig_detail, use_container_width=True)

            st.markdown(
                f"<p style='color:#cbd5e1; font-size:13px; font-weight:600; margin:8px 0;'>{drill_name} - {selected_dim} 明细</p>",
                unsafe_allow_html=True
            )
            st.dataframe(
                detail_df,
                use_container_width=True,
                hide_index=True,
                column_config={x_col: st.column_config.TextColumn(x_col), y_col: st.column_config.NumberColumn(y_col)},
            )
        else:
            st.info("暂无该指标的明细数据")

# ========== 核心指标趋势 ==========
with st.container(border=True):
    st.markdown(f'<div class="panel-header">核心指标分时趋势 <span style="font-size:11px; color:#cbd5e1; font-weight:400; margin-left:6px;">{query_date}</span></div>', unsafe_allow_html=True)

    trend_df = generate_trend_data(24, query_date)
    col1, col2, col3 = st.columns(3)
    chart_configs = [
        (col1, "销售额每日趋势", "销售额", "#3b82f6", "rgba(59,130,246,0.15)"),
        (col2, "订单量每日趋势", "订单量", "#8b5cf6", "rgba(139,92,246,0.15)"),
        (col3, "付款订单每日趋势", "付款订单", "#ec4899", "rgba(236,72,153,0.15)"),
    ]
    for i, (col, title, col_name, color, fill_color) in enumerate(chart_configs):
        with col:
            st.markdown(f"<p style='color:#cbd5e1; font-size:13px; font-weight:600; margin-bottom:8px;'>{title}</p>", unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_df["时间"], y=trend_df[col_name], mode="lines",
                line=dict(color=color, width=2.5), fill="tozeroy", fillcolor=fill_color,
                hovertemplate=f"<b>%{{x}}</b><br>{col_name}: %{{y}}<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=30), height=220,
                xaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=10), tickangle=45, nticks=8),
                yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.5)", tickfont=dict(color="#cbd5e1", size=10), zeroline=False),
                showlegend=False, hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True, key=f"trend_{i}")

# ========== 维度拆解分析 ==========
with st.container(border=True):
    st.markdown('<div class="panel-header">维度拆解分析</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<p style='color:#cbd5e1; font-size:13px; font-weight:600; margin-bottom:8px;'>全国订单分布热力图</p>", unsafe_allow_html=True)
        prov_df = generate_province_distribution().head(15)
        prov_colors = ["#1e3a5f", "#1e40af", "#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#dbeafe", "#eff6ff"]
        prov_color_list = [prov_colors[min(i, len(prov_colors) - 1)] for i in range(len(prov_df))]
        fig_map = go.Figure()
        fig_map.add_trace(go.Bar(
            y=list(reversed(prov_df["省份"].tolist())), x=list(reversed(prov_df["订单量"].tolist())), orientation="h",
            marker=dict(color=list(reversed(prov_color_list)), line=dict(color="#1e293b", width=1)),
            text=[f"{v:,}" for v in reversed(prov_df["订单量"].tolist())], textposition="outside", textfont=dict(color="#cbd5e1", size=11),
            hovertemplate="<b>%{y}</b><br>订单量: %{x}<extra></extra>",
        ))
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=60, r=40, t=10, b=10), height=280,
            xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=12)),
            bargap=0.25,
        )
        st.plotly_chart(fig_map, use_container_width=True, key="map_chart_main")

    with col2:
        st.markdown("<p style='color:#cbd5e1; font-size:13px; font-weight:600; margin-bottom:8px;'>订单状态占比</p>", unsafe_allow_html=True)
        channel_df = generate_channel_data(query_date)
        fig_channel = go.Figure(data=[go.Pie(
            labels=channel_df["渠道"], values=channel_df["订单量"], hole=0.6,
            textinfo="label+percent", textfont=dict(size=11, color="#e2e8f0"),
            marker=dict(colors=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"], line=dict(color="#1e293b", width=2)),
            hovertemplate="<b>%{label}</b><br>订单量: %{value}<br>占比: %{percent}<extra></extra>",
        )])
        fig_channel.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=10), height=280, showlegend=False,
            annotations=[dict(
                text=f"<b>{channel_df['订单量'].sum()}</b><br><span style='font-size:11px;color:#cbd5e1'>总订单</span>",
                x=0.5, y=0.5, font_size=18, font_color="#e2e8f0", showarrow=False,
            )],
        )
        st.plotly_chart(fig_channel, use_container_width=True, key="channel_chart_main")

    with col3:
        st.markdown("<p style='color:#cbd5e1; font-size:13px; font-weight:600; margin-bottom:8px;'>省份销售 TOP10</p>", unsafe_allow_html=True)
        top_df = generate_top_products(query_date)
        colors_top = ["#f59e0b" if i == 0 else "#3b82f6" for i in range(len(top_df))]
        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            y=list(reversed(top_df["商品名称"].tolist())), x=list(reversed(top_df["销量"].tolist())), orientation="h",
            marker=dict(color=list(reversed(colors_top)), line=dict(color="#1e293b", width=1)),
            text=[f"{v}" for v in reversed(top_df["销量"].tolist())], textposition="outside", textfont=dict(color="#cbd5e1", size=10),
            hovertemplate="<b>%{y}</b><br>销量: %{x}<extra></extra>",
        ))
        fig_top.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=120, r=30, t=10, b=10), height=280,
            xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1", size=10)),
            bargap=0.3,
        )
        st.plotly_chart(fig_top, use_container_width=True, key="top_chart_main")

# ========== 监控中心与告警 ==========
with st.container(border=True):
    st.markdown('<div class="panel-header">监控中心与告警</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("<p style='color:#cbd5e1; font-size:13px; font-weight:600; margin-bottom:10px;'>告警监控</p>", unsafe_allow_html=True)

        alert_df = generate_alert_data(query_date)

        # 计算各级别数量
        high_count = len(alert_df[alert_df["level"] == "高危"])
        mid_count = len(alert_df[alert_df["level"] == "中危"])
        low_count = len(alert_df[alert_df["level"] == "低危"])

        alert_stats_html = f"""
        <div style="display:flex; gap:10px; margin-bottom:14px;">
            <div style="flex:1; background:#7f1d1d; border:1px solid #b91c1c; border-radius:8px; padding:10px; text-align:center;">
                <div style="font-size:20px; font-weight:800; color:#fca5a5;">{high_count}</div>
                <div style="font-size:11px; color:#f87171; margin-top:2px;">高危告警</div>
            </div>
            <div style="flex:1; background:#713f12; border:1px solid #ca8a04; border-radius:8px; padding:10px; text-align:center;">
                <div style="font-size:20px; font-weight:800; color:#fde047;">{mid_count}</div>
                <div style="font-size:11px; color:#facc15; margin-top:2px;">中危告警</div>
            </div>
            <div style="flex:1; background:#1e3a5f; border:1px solid #3b82f6; border-radius:8px; padding:10px; text-align:center;">
                <div style="font-size:20px; font-weight:800; color:#93c5fd;">{low_count}</div>
                <div style="font-size:11px; color:#60a5fa; margin-top:2px;">低危告警</div>
            </div>
        </div>
        """
        st.html(alert_stats_html)

        for _, row in alert_df.iterrows():
            level = row["level"]
            level_color = {"高危": "#ef4444", "中危": "#f59e0b", "低危": "#3b82f6"}[level]
            level_bg = {"高危": "#7f1d1d", "中危": "#713f12", "低危": "#1e3a5f"}[level]
            status_color = {"未处理": "#ef4444", "处理中": "#f59e0b", "已处理": "#10b981"}[row["status"]]
            status_bg = {"未处理": "#7f1d1d", "处理中": "#713f12", "已处理": "#064e3b"}[row["status"]]

            alert_item_html = f"""
            <div style="background:#0f172a; border-radius:6px; padding:10px 12px; margin-bottom:8px; border-left:3px solid {level_color};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="background:{level_bg}; color:{level_color}; padding:1px 8px; border-radius:3px; font-size:10px; font-weight:600;">{level}</span>
                        <span style="color:#e2e8f0; font-weight:600; font-size:12px;">{row["type"]}</span>
                    </div>
                    <span style="color:#cbd5e1; font-size:10px;">{row["time"]}</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#cbd5e1; font-size:11px;">{row["value"]}</span>
                    <span style="background:{status_bg}; color:{status_color}; padding:2px 8px; border-radius:3px; font-size:10px; font-weight:600;">{row["status"]}</span>
                </div>
            </div>
            """
            st.html(alert_item_html)

    with col_right:
        st.markdown("<p style='color:#cbd5e1; font-size:13px; font-weight:600; margin-bottom:10px;'>订单流水</p>", unsafe_allow_html=True)
        order_df = generate_order_stream(8)

        table_html = """
        <table style="width:100%; border-collapse:collapse; font-size:12px;">
            <thead>
                <tr style="background:#1e293b;">
                    <th style="padding:8px 10px; text-align:left; color:#cbd5e1; font-weight:600; border-bottom:1px solid #334155;">订单编号</th>
                    <th style="padding:8px 10px; text-align:left; color:#cbd5e1; font-weight:600; border-bottom:1px solid #334155;">时间</th>
                    <th style="padding:8px 10px; text-align:right; color:#cbd5e1; font-weight:600; border-bottom:1px solid #334155;">金额</th>
                    <th style="padding:8px 10px; text-align:center; color:#cbd5e1; font-weight:600; border-bottom:1px solid #334155;">状态</th>
                </tr>
            </thead>
            <tbody>
        """
        status_colors = {
            "已完成": ("#064e3b", "#10b981"), "配送中": ("#713f12", "#f59e0b"),
            "待发货": ("#1e3a5f", "#3b82f6"), "已取消": ("#7f1d1d", "#ef4444"),
        }
        for _, row in order_df.iterrows():
            bg, color = status_colors.get(row["订单状态"], ("#1e293b", "#cbd5e1"))
            order_id = row["订单编号"][-8:] if len(str(row["订单编号"])) > 8 else row["订单编号"]
            table_html += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="padding:8px 10px; color:#cbd5e1; font-family:monospace; font-size:11px;">{order_id}</td>
                <td style="padding:8px 10px; color:#cbd5e1; font-size:11px;">{row["下单时间"]}</td>
                <td style="padding:8px 10px; color:#e2e8f0; text-align:right; font-weight:600;">{row["消费金额"]}</td>
                <td style="padding:8px 10px; text-align:center;">
                    <span style="background:{bg}; color:{color}; padding:2px 8px; border-radius:3px; font-size:10px; font-weight:600;">{row["订单状态"]}</span>
                </td>
            </tr>
            """
        table_html += "</tbody></table>"
        st.html(table_html)

# ========== 底部信息 ==========
st.markdown(f"""
<div style="text-align:center; padding:12px; color:#cbd5e1; font-size:11px; border-top:1px solid rgba(100,180,255,0.1); margin-top:12px;">
    数据来源: 天猫订单成交数据（天池公开数据集 28010 单） | 数据日期: {query_date}
</div>
""", unsafe_allow_html=True)

# 自动刷新
if auto_refresh:
    interval_seconds = int(refresh_interval.replace("s", ""))
    time.sleep(interval_seconds)
    st.rerun()
