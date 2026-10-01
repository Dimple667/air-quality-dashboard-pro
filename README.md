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
│   ├── app.py                # Flask 服务（HTTP 层：/api/* 前缀、统一响应、全局异常处理）
│   ├── air_quality_core.py   # 纯业务逻辑：建库、演示数据生成、聚合查询（不依赖 Flask）
│   ├── air_quality.db        # SQLite 演示数据库（自动初始化，请保留）
│   └── requirements.txt
├── netlify/
│   ├── functions/api.mjs     # 线上版 /api/* 接口（Netlify Function）
│   └── data/                 # 构建期生成的快照，已被 .gitignore 忽略
├── scripts/
│   └── export_snapshot.py    # 构建期把数据导出为函数可 import 的 JS 模块
├── netlify.toml              # Netlify 构建设置与 /api/* 重写规则
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

> `air_quality_core.py` 是业务逻辑的唯一来源：本地 Flask 服务与 Netlify 构建脚本
> 都复用它，所以两边的数据口径不会跑偏。

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

## 部署到 Netlify

### 为什么不是直接部署 Flask

Netlify Functions **不支持 Python 运行时**，只支持 JavaScript / TypeScript / Go；Python 只能在
构建阶段使用。因此线上架构是：

```
构建阶段（Python 可用）
  scripts/export_snapshot.py
    用固定种子重新生成演示数据（日期窗口锚定构建当天）
    -> 跑完聚合逻辑
    -> 产出 netlify/data/snapshot.mjs

运行阶段（Netlify Function, JS）
  GET /api/health
  GET /api/cities
  GET /api/dashboard_data?city=北京     <- 由 netlify.toml 从 /api/* 重写过来
```

接口的响应结构与 `backend/app.py` 完全一致，所以**前端代码一行都不用改**
（`http.ts` 里的 `baseURL: '/api'` 在开发和生产下都成立）。

副作用是趋势图每天都是"最近 14 天"，不会随仓库里那份数据一起变旧。

### 部署步骤

1. 把改动推到 GitHub。
2. 打开 [Netlify](https://app.netlify.com) → **Add new site** → **Import an existing project** →
   选 GitHub 仓库。
3. 构建设置**留空即可**：仓库根目录的 `netlify.toml` 已经写好
   （build command、publish 目录、Node 版本、`/api/*` 重写规则）。
4. 点 Deploy。之后每次 push 到默认分支都会自动重新部署。

### 本地预览线上形态

```bash
# 生成函数需要的快照（用哪个 Python 都行，脚本只依赖标准库）
backend/.venv/Scripts/python.exe scripts/export_snapshot.py   # Windows
python3 scripts/export_snapshot.py                            # macOS / Linux

npx netlify-cli dev      # 本地起一个和线上一致的站点
```

> Netlify 构建机上 `python3` 直接可用（`netlify.toml` 里已声明 `PYTHON_VERSION`）。
> Windows 本地如果没有全局 Python，用上面 venv 里的解释器即可。

`netlify/data/` 是构建产物，已被 `.gitignore` 忽略，所以本地跑 `netlify dev` 前必须先执行导出脚本。

## 说明

- `backend/air_quality.db` 仅包含演示数据（城市 AQI 模拟数据），无敏感信息，请保留在仓库中保证开箱即用。
  它是**本地开发**的数据源；线上数据由构建脚本按固定种子重新生成。
- 中国地图 GeoJSON 运行时从阿里云 DataV 在线加载，若加载失败会自动降级为散点视图。
- 数据源替换：将 `backend/air_quality_core.py` 中 `generate_rows()` 的演示数据逻辑替换为你的
  爬虫写入逻辑即可，Flask 与 Netlify 两侧会同时生效。
