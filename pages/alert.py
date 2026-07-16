import streamlit as st
from utils.data_generator import generate_alert_data

st.set_page_config(page_title="告警记录", page_icon="", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color:#e2e8f0; margin-bottom:20px;'>告警记录</h2>", unsafe_allow_html=True)

alert_df = generate_alert_data()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%); 
                border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #b91c1c;">
        <div style="font-size: 32px; font-weight: 800; color: #fca5a5;">1</div>
        <div style="font-size: 14px; color: #f87171; margin-top: 4px;">高危告警</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #713f12 0%, #a16207 100%); 
                border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #ca8a04;">
        <div style="font-size: 32px; font-weight: 800; color: #fde047;">2</div>
        <div style="font-size: 14px; color: #facc15; margin-top: 4px;">中危告警</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%); 
                border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #3b82f6;">
        <div style="font-size: 32px; font-weight: 800; color: #93c5fd;">2</div>
        <div style="font-size: 14px; color: #60a5fa; margin-top: 4px;">低危告警</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div style='background:#1e293b; border-radius:12px; padding:16px; border:1px solid #334155;'>" 
            "<h4 style='color:#94a3b8; margin:0 0 12px 0;'>告警列表</h4>", unsafe_allow_html=True)

for _, row in alert_df.iterrows():
    level_color = {"高危": "#ef4444", "中危": "#f59e0b", "低危": "#3b82f6"}[row["level"]]
    level_bg = {"高危": "#7f1d1d", "中危": "#713f12", "低危": "#1e3a5f"}[row["level"]]
    status_color = {"未处理": "#ef4444", "处理中": "#f59e0b", "已处理": "#10b981"}[row["status"]]

    st.markdown(f"""
    <div style="background: #0f172a; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; 
                border-left: 4px solid {level_color}; display: flex; justify-content: space-between; align-items: center;">
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="background: {level_bg}; color: {level_color}; padding: 2px 10px; border-radius: 4px; font-size: 12px; font-weight: 600;">{row["level"]}</span>
                <span style="color: #e2e8f0; font-weight: 600; font-size: 14px;">{row["type"]}</span>
                <span style="color: #64748b; font-size: 12px;">{row["time"]}</span>
            </div>
            <div style="color: #94a3b8; font-size: 13px;">{row["value"]}</div>
        </div>
        <div style="margin-left: 20px;">
            <span style="background: {'#7f1d1d' if row['status']=='未处理' else '#713f12' if row['status']=='处理中' else '#064e3b'}; 
                         color: {status_color}; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600;">{row["status"]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
