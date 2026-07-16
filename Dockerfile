# 企业数据智能监控大屏 - 容器化部署
FROM python:3.11-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY . .

# Streamlit 配置
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

EXPOSE 8501

# 同时启动 Flask 后端 (5000) 与 Streamlit 前端 (8501)
# 开发环境可直接 `streamlit run app.py`；生产环境建议用 gunicorn 拉起后端
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
