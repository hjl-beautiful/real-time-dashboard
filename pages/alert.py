import streamlit as st
from utils.data_generator import generate_alert_data

st.set_page_config(page_title="告警记录", page_icon="", layout="wide")

st.markdown("<h2 style='color:#e2e8f0; margin-bottom:20px;'>告警记录</h2>", unsafe_allow_html=True)

alert_df = generate_alert_data()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("高危告警", "1", delta=None)
with col2:
    st.metric("中危告警", "2", delta=None)
with col3:
    st.metric("低危告警", "2", delta=None)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:13px; font-weight:600; margin-bottom:12px;'>告警列表</p>", unsafe_allow_html=True)

for _, row in alert_df.iterrows():
    level_color = {"高危": "#ef4444", "中危": "#f59e0b", "低危": "#3b82f6"}[row["level"]]
    level_bg = {"高危": "#7f1d1d", "中危": "#713f12", "低危": "#1e3a5f"}[row["level"]]
    status_color = {"未处理": "#ef4444", "处理中": "#f59e0b", "已处理": "#10b981"}[row["status"]]
    status_bg = {"未处理": "#7f1d1d", "处理中": "#713f12", "已处理": "#064e3b"}[row["status"]]

    with st.container():
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"<span style='background:{level_bg}; color:{level_color}; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600;'>{row['level']}</span> <b style='color:#e2e8f0; font-size:13px;'>{row['type']}</b> <span style='color:#64748b; font-size:11px;'>{row['time']}</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#94a3b8; font-size:12px; margin:4px 0 0 0;'>{row['value']}</p>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='text-align:right;'><span style='background:{status_bg}; color:{status_color}; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600;'>{row['status']}</span></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1e293b; margin:8px 0;'>", unsafe_allow_html=True)
