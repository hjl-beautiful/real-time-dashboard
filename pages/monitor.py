import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_generator import generate_kpi_data

st.set_page_config(page_title="实时监控", page_icon="", layout="wide")

st.markdown("<h2>实时监控</h2>", unsafe_allow_html=True)

st.markdown("### 区域销售分布")

regions = ["华北", "华东", "华南", "华中", "西南", "西北", "东北"]
region_sales = [320, 450, 380, 280, 220, 150, 180]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(regions, region_sales, color=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a'])
ax.set_title('各区域销售额分布', fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel('销售额(万元)')
ax.grid(True, alpha=0.3, axis='y')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height}',
            ha='center', va='bottom', fontsize=10)

plt.tight_layout()
st.pyplot(fig)

st.markdown("---")

st.markdown("### 产品类别销售占比")

categories = ["电子产品", "服装", "食品", "家居", "美妆", "图书"]
cat_sales = [35, 25, 15, 12, 8, 5]

fig, ax = plt.subplots(figsize=(8, 8))
colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
wedges, texts, autotexts = ax.pie(cat_sales, labels=categories, autopct='%1.1f%%',
                                     colors=colors, startangle=90)
ax.set_title('产品类别销售占比', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
st.pyplot(fig)
