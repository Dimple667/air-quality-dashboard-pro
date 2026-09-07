# Air Quality Dashboard Pro

面向前端求职作品集的前后端分离空气质量可视化看板项目。

## 技术栈

- 前端：Vue 3 / TypeScript / Vite / Pinia / Axios / ECharts
- 后端：Flask / SQLite

## 项目功能

- 空气质量数据展示（AQI、PM2.5、PM10 等指标）
- 指标统计（监测城市、平均 AQI、优良/污染城市数量）
- 趋势分析（近 7 日 AQI / PM2.5 折线趋势）
- ECharts 可视化（地图散点、柱状图、饼图、折线图）
- 条件筛选（城市下拉、地图/排名点击联动）
- 前后端分离（前端经 Vite proxy 请求 Flask API）
- SQLite 数据读取（首次启动自动初始化演示数据）

## 目录结构

```
air-quality-vue-dashboard-pro/
├── backend/
│   ├── app.py            # Flask 服务（/api/* 统一前缀、统一响应结构、全局异常处理）
│   ├── air_quality.db    # SQLite 演示数据库（自动初始化，请保留）
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/          # Axios 统一封装（baseURL: /api + 请求/响应拦截器）
    │   ├── components/   # 图表与 UI 组件（ECharts 统一生命周期封装）
    │   ├── composables/  # useECharts 组合式函数
    │   ├── stores/       # Pinia（筛选条件 / 核心数据 / loading / error）
    │   ├── types/        # TypeScript 类型定义
    │   └── views/        # Dashboard 页面
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts    # dev server proxy: /api -> http://127.0.0.1:5000
```

## 运行方式

### 后端

```bash
cd backend
python -m venv .venv                # 可选，建议使用虚拟环境隔离依赖
.venv\Scripts\activate              # Windows；macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Flask 默认启动在 `http://127.0.0.1:5000`，所有接口统一以 `/api` 开头：

- `GET /api/health` — 健康检查
- `GET /api/cities` — 城市列表
- `GET /api/dashboard_data?city=北京` — 看板核心数据

统一响应结构：

```json
{ "code": 0, "message": "success", "data": { ... } }
```

异常时返回（不会把 Python traceback 暴露给前端）：

```json
{ "code": 500, "message": "服务器内部错误", "data": null }
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端默认通过 Vite proxy 请求 Flask：

```
/api -> http://127.0.0.1:5000
```

打开 `http://localhost:5173` 即可访问看板。

### 构建

```bash
cd frontend
npm run build
```

产物输出到 `frontend/dist/`。

## 说明

- `backend/air_quality.db` 仅包含演示数据（城市 AQI 模拟数据），无敏感信息，请保留在仓库中保证开箱即用。
- 中国地图 GeoJSON 运行时从阿里云 DataV 在线加载，若加载失败会自动降级为散点视图。
- 数据源替换：将 `backend/app.py` 中 `init_db()` 的演示数据逻辑替换为你的爬虫写入逻辑即可。
