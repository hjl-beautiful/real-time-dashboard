import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import generate_trend_data, generate_channel_data, generate_map_data

st.set_page_config(page_title="实时监控", page_icon="", layout="wide")

st.markdown("<h2 style='color:#e2e8f0; margin-bottom:20px;'>实时监控</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("<p style='color:#94a3b8; font-size:13px; font-weight:600; margin-bottom:10px;'>全国用户分布热力图</p>", unsafe_allow_html=True)
    map_df = generate_map_data()
    fig_map = px.bar(
        map_df.head(10).sort_values("活跃用户", ascending=True),
        x="活跃用户", y="省份", orientation="h",
        color="活跃用户", color_continuous_scale="Blues",
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=20, t=10, b=10), height=380,
        xaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8")),
        yaxis=dict(showgrid=False, tickfont=dict(color="#e2e8f0")),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_map, use_container_width=True, key="map_chart")

with col2:
    st.markdown("<p style='color:#94a3b8; font-size:13px; font-weight:600; margin-bottom:10px;'>渠道订单占比</p>", unsafe_allow_html=True)
    channel_df = generate_channel_data()
    fig_channel = go.Figure(data=[go.Pie(
        labels=channel_df["渠道"], values=channel_df["订单量"], hole=0.55,
        textinfo="label+percent", textfont=dict(size=12, color="#e2e8f0"),
        marker=dict(colors=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"], line=dict(color="#1e293b", width=2)),
        hovertemplate="<b>%{label}</b><br>订单量: %{value}<br>占比: %{percent}<extra></extra>",
    )])
    fig_channel.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=0), height=380, showlegend=False,
        annotations=[dict(text="订单分布", x=0.5, y=0.5, font_size=16, font_color="#94a3b8", showarrow=False)],
    )
    st.plotly_chart(fig_channel, use_container_width=True, key="channel_chart")

st.markdown("<p style='color:#94a3b8; font-size:13px; font-weight:600; margin:16px 0 10px 0;'>产品类别销售占比</p>", unsafe_allow_html=True)
categories = ["数码电子", "家居生活", "服饰鞋包", "美妆护肤", "食品饮料", "运动户外"]
cat_values = [35, 22, 18, 12, 8, 5]
cat_colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]
fig_cat = go.Figure()
fig_cat.add_trace(go.Bar(
    x=categories, y=cat_values,
    marker=dict(color=cat_colors, line=dict(color="#1e293b", width=1)),
    text=[f"{v}%" for v in cat_values], textposition="outside",
    textfont=dict(color="#e2e8f0", size=13),
    hovertemplate="<b>%{x}</b><br>占比: %{y}%<extra></extra>",
))
fig_cat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=20, b=40), height=280,
    xaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8", size=12)),
    yaxis=dict(showgrid=True, gridcolor="#334155", tickfont=dict(color="#94a3b8"), showticklabels=False, range=[0, 45]),
    bargap=0.4,
)
st.plotly_chart(fig_cat, use_container_width=True, key="cat_chart")
