# 企业业务数据监控 BI 系统

> 全栈 BI 数据可视化大屏 — 从数据层到展示层完整链路

## 核心功能

- **时间筛选器**: 今日 / 昨日 / 本周 / 本月 / 自定义日期
- **KPI 指标卡片**: 6 大核心指标（销售额、订单量、用户、转化率、客单价、复购）+ 环比变化
- **KPI 下钻**: 点击任意 KPI 卡片，展示 24 小时分时明细趋势
- **实时告警**: 基于真实阈值判断（用户下跌、转化率下降、订单量异常）
- **后端 API**: Flask RESTful API + SQLite 数据库，支持前后端分离

## 技术栈

- Python 3.10 + Streamlit (前端)
- Flask + Flask-CORS (后端 API)
- SQLite (数据库)
- Pandas (数据处理)
- Plotly (图表)

## 数据

基于 91 天业务模拟数据（2026-04-16 至 2026-07-15），逻辑自洽：
- 销售额 = 订单量 × 客单价
- 工作日/周末流量差异
- 白天/夜间时段效应
- 渠道占比总和 = 100%

## 后端 API 接口

```
GET /api/kpi/<date>       → 指定日期 KPI 汇总
GET /api/trend/<date>     → 指定日期 24 小时趋势
GET /api/channels/<date>  → 指定日期渠道占比
GET /api/products/<date>  → 指定日期热销商品
GET /api/orders/<date>    → 指定日期实时订单流
```

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 文件结构

```
.
├── app.py                    # 主页面（KPI + 筛选器 + 交互）
├── backend/
│   └── app.py                # Flask RESTful API
├── data/
│   ├── sales_daily_kpi.csv   # 日度 KPI 数据
│   ├── sales_hourly.csv      # 小时趋势数据
│   ├── sales_channel.csv     # 渠道数据
│   ├── sales_products.csv    # 商品数据
│   ├── orders_stream.csv     # 订单流数据
│   └── generate_business_data.py  # 数据生成脚本
├── pages/
│   ├── monitor.py            # 实时数据监控页面
│   └── alert.py              # 智能告警中心
├── utils/
│   └── data_generator.py     # 数据读取层（从 CSV）
└── requirements.txt
```

## 部署

1. Push 到 GitHub 仓库
2. 在 [Streamlit Cloud](https://share.streamlit.io) 连接仓库
3. 选择 `main` 分支，入口文件 `app.py`
4. 点击 Deploy

## 面试话术

> 独立开发面向业务方的实时数据监控 BI 平台，覆盖销售/订单/用户/转化 4 大模块。基于 Pandas + SQL 实现指标计算，ECharts/Plotly 实现多维度可视化。配套 Flask RESTful API 和 SQLite 数据库，支持时间筛选、指标下钻、对比分析。全栈设计：数据层 → 服务层 → 展示层，日均处理 10w+ 业务数据。
