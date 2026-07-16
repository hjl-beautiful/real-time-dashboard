import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="告警记录", page_icon="", layout="wide")

st.markdown("<h2>告警记录</h2>", unsafe_allow_html=True)

alert_data = {
    "时间": [
        (datetime.now() - timedelta(minutes=5)).strftime("%H:%M"),
        (datetime.now() - timedelta(minutes=15)).strftime("%H:%M"),
        (datetime.now() - timedelta(minutes=30)).strftime("%H:%M"),
        (datetime.now() - timedelta(minutes=45)).strftime("%H:%M"),
        (datetime.now() - timedelta(minutes=60)).strftime("%H:%M"),
    ],
    "告警类型": ["销售额异常", "订单量下降", "用户流失", "系统延迟", "库存不足"],
    "级别": ["严重", "警告", "警告", "一般", "严重"],
    "状态": ["已处理", "已处理", "处理中", "已处理", "未处理"],
    "处理人": ["张三", "李四", "王五", "张三", "-"]
}

df_alerts = pd.DataFrame(alert_data)

st.dataframe(df_alerts, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 告警统计")

col1, col2, col3 = st.columns(3)
col1.metric("今日告警", 12, delta=3)
col2.metric("严重告警", 3, delta=-1)
col3.metric("未处理", 2, delta=0)
