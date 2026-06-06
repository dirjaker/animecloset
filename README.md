<div align="center">

# 👗 衫 间

### 新中式 AI 穿搭助手

[![功能](https://img.shields.io/badge/功能-6-blue?style=flat-square)]()
[![AI](https://img.shields.io/badge/AI-生成-green?style=flat-square)]()
[![技术](https://img.shields.io/badge/技术-Naive%20UI-orange?style=flat-square)]()
[![更新](https://img.shields.io/badge/更新-2026.06-red?style=flat-square)]()

*智能抠图 · 衣橱管理 · 天气穿搭推荐 · AI 插画生成 · 日历穿搭记录 · 虚拟形象系统*

</div>

---

> 基于 AI 视觉识别与大模型能力的智能衣柜管理与穿搭推荐系统，以新中式暖木风格呈现。

---

## 项目概览

| 项目信息 | 说明 |
|---|---|
| 项目名称 | 衫间（AnimeCloset） |
| 项目定位 | 新中式 AI 穿搭助手 |
| 核心理念 | 将 AI 视觉理解、天气数据、日程管理与动漫插画生成融为一体，打造个性化穿搭体验 |
| 前端框架 | Vue 3 + Vite + Naive UI |
| 后端框架 | FastAPI + SQLAlchemy (async) + SQLite |
| AI 能力 | DeepSeek Vision（图像自动标注）、通义万相（插画生成）、rembg（智能抠图） |
| 开源协议 | MIT |

---

## 功能特性

### 核心功能

| 功能模块 | 描述 | 技术实现 |
|---|---|---|
| 智能图片裁剪 | 上传服装照片后自动识别并裁剪主体区域，去除背景 | rembg 抠图 + Pillow 图像处理 |
| 自动标签生成 | 对衣物图片进行 AI 视觉分析，自动识别品类、颜色、风格、季节等属性 | DeepSeek Vision API |
| 衣柜管理 | 可视化管理所有衣物，支持按标签/分类筛选、搜索、编辑、删除 | 前端 Naive UI 组件 + 后端 CRUD API |
| 天气穿搭推荐 | 根据用户当前城市天气数据，结合衣物标签智能推荐穿搭方案 | 天气 API + LLM 推荐逻辑 |
| 日历视图 | 以日历形式查看每日穿搭记录，支持回顾与规划，正方形格子适配虚拟形象 | JS ResizeObserver + CSS 变量动态计算 |
| AI 穿搭插画 | 将推荐穿搭方案生成动漫风格插画，可保存与分享 | 通义万相 API |

### 辅助功能

| 功能 | 描述 |
|---|---|
| 穿搭历史记录 | 自动保存每日穿搭记录，支持按日期回溯 |
| 多条件筛选 | 按季节、场景、颜色、风格等多维度筛选衣物 |
| 响应式布局 | 适配桌面端与移动端浏览 |
| 数据本地化 | SQLite 本地存储，无需额外数据库服务 |

---

## 技术栈

### 后端

| 技术 | 用途 |
|---|---|
| Python 3.11+ | 主语言 |
| FastAPI | 异步 Web 框架，提供 RESTful API |
| SQLAlchemy 2.0 (async) | 异步 ORM，数据库建模与查询 |
| SQLite | 轻量级本地数据库 |
| Alembic | 数据库迁移管理 |
| rembg | 基于 U²-Net 的图像抠图 |
| Pillow | 图像裁剪与格式转换 |
| httpx | 异步 HTTP 客户端，调用外部 AI API |

### 前端

| 技术 | 用途 |
|---|---|
| Vue 3 | 响应式 UI 框架 (Composition API + `<script setup>`) |
| Vite | 极速开发构建工具 |
| Naive UI | Vue 3 组件库，提供丰富 UI 组件 |
| Vue Router | 路由管理 |
| Axios | HTTP 请求封装 |

### 外部 API

| API | 用途 |
|---|---|
| DeepSeek Vision | 衣物图像识别与自动标签生成 |
| 通义万相 (Tongyi Wanxiang) | 动漫风格穿搭插画生成 |
| 天气 API | 获取实时天气数据用于穿搭推荐 |

---

## 系统架构

```
┌─────────────────────────────────────────────────┐
│                   前端 (Vue 3)                    │
│     Vite + Naive UI + Vue Router                 │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / REST API
                       ▼
┌─────────────────────────────────────────────────┐
│                后端 (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 衣物管理  │  │ 穿搭推荐  │  │ 日历/历史记录 │  │
│  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       │              │                │          │
│  ┌────▼──────────────▼────────────────▼───────┐  │
│  │         SQLAlchemy Async ORM (SQLite)       │  │
│  └────────────────────────────────────────────┘  │
│       │              │                │          │
│  ┌────▼─────┐  ┌─────▼─────┐  ┌──────▼───────┐  │
│  │  rembg   │  │ DeepSeek  │  │  通义万相 API │  │
│  │  抠图服务 │  │ Vision    │  │  插画生成     │  │
│  └──────────┘  └───────────┘  └──────────────┘  │
└─────────────────────────────────────────────────┘
```

**数据流说明：**

1. 用户上传衣物图片 → rembg 智能抠图 → DeepSeek Vision 自动标注 → 存入数据库
2. 用户请求穿搭推荐 → 读取天气数据 + 衣物标签 → LLM 生成推荐方案
3. 用户生成插画 → 将穿搭描述发送至通义万相 API → 返回动漫风格图片

---

## 快速开始

### 环境要求

| 依赖 | 最低版本 |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| pnpm / npm | pnpm 推荐 |

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境并激活
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys：
#   DEEPSEEK_API_KEY=your_deepseek_key
#   TONGYI_API_KEY=your_tongyi_key
#   WEATHER_API_KEY=your_weather_key

# 初始化数据库
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

前端默认运行在 `http://localhost:5173`，后端 API 文档位于 `http://localhost:8000/docs`。

---

## 项目结构

```
animecloset/
├── backend/
│   ├── app/
│   │   ├── api/                    # API 路由
│   │   │   ├── auth.py             # 认证接口（登录/注册）
│   │   │   ├── garments.py         # 衣物管理接口
│   │   │   ├── outfits.py          # 穿搭记录与日历接口
│   │   │   ├── recommend.py        # 穿搭推荐接口
│   │   │   ├── stats.py            # 数据统计接口
│   │   │   └── user.py             # 用户信息接口
│   │   ├── core/
│   │   │   ├── config.py           # 配置管理
│   │   │   ├── database.py         # 数据库连接与会话
│   │   │   └── security.py         # JWT 认证与密码哈希
│   │   ├── models/                 # SQLAlchemy 数据模型
│   │   │   ├── garment.py          # 衣物模型
│   │   │   ├── outfit.py           # 穿搭记录模型
│   │   │   └── user.py             # 用户模型
│   │   ├── schemas/                # Pydantic 请求/响应模型
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── bg_remove.py        # rembg 抠图处理
│   │   │   ├── llm_tag.py          # DeepSeek Vision 标注
│   │   │   ├── recommend.py        # 穿搭推荐逻辑
│   │   │   ├── task_manager.py     # 异步任务管理
│   │   │   ├── wanx.py             # 通义万相插画生成
│   │   │   └── weather.py          # 天气数据获取
│   │   └── main.py                 # FastAPI 应用入口
│   ├── alembic/                    # 数据库迁移文件
│   ├── uploads/                    # 上传图片存储
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/                  # 页面组件
│   │   │   ├── WardrobeView.vue    # 衣柜管理页
│   │   │   ├── RecommendView.vue   # 穿搭推荐页
│   │   │   ├── CalendarView.vue    # 日历视图页（正方形格子 + ResizeObserver）
│   │   │   ├── ProfileView.vue     # 个人中心页
│   │   │   └── LoginView.vue       # 登录页
│   │   ├── api/                    # Axios 请求封装
│   │   ├── stores/                 # 状态管理
│   │   │   └── auth.js             # 认证状态
│   │   ├── router/                 # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── README.md
```

---

## API 端点

### 认证

| 方法 | 路径 | 描述 |
|---|---|---|
| `POST` | `/api/auth/register` | 用户注册 |
| `POST` | `/api/auth/login` | 用户登录 |

### 衣物管理

| 方法 | 路径 | 描述 |
|---|---|---|
| `GET` | `/api/garments` | 获取衣物列表（支持分页与筛选） |
| `GET` | `/api/garments/{id}` | 获取单件衣物详情 |
| `POST` | `/api/garments/upload` | 上传新衣物（图片 + 自动抠图标注） |
| `GET` | `/api/garments/status/{task_id}` | 查询上传任务状态 |
| `PUT` | `/api/garments/{id}` | 更新衣物信息 |
| `DELETE` | `/api/garments/{id}` | 删除衣物 |

### 穿搭记录

| 方法 | 路径 | 描述 |
|---|---|---|
| `POST` | `/api/outfits` | 保存穿搭方案 |
| `GET` | `/api/outfits/calendar` | 获取日历穿搭记录 |
| `POST` | `/api/outfits/{id}/illustration` | 生成穿搭插画 |

### 穿搭推荐

| 方法 | 路径 | 描述 |
|---|---|---|
| `POST` | `/api/recommend` | 获取穿搭推荐方案 |

### 数据统计

| 方法 | 路径 | 描述 |
|---|---|---|
| `GET` | `/api/stats/wardrobe` | 衣柜统计数据 |
| `GET` | `/api/stats/cold-palace` | 冷宫衣物（长期未穿） |
| `GET` | `/api/stats/wear-ranking` | 穿着次数排行 |

### 用户信息

| 方法 | 路径 | 描述 |
|---|---|---|
| `GET` | `/api/user/me` | 获取当前用户信息 |
| `GET` | `/api/user/avatar` | 获取虚拟形象配置 |
| `PUT` | `/api/user/avatar` | 更新虚拟形象配置 |

---

## 开发说明

### 后端开发

- 所有数据库操作使用 SQLAlchemy 2.0 异步语法 (`async/await`)
- API 路由遵循 RESTful 规范，返回统一响应格式
- 外部 API 调用通过 `httpx.AsyncClient` 实现异步请求
- 图片上传后统一存储在 `uploads/` 目录，数据库存储相对路径

### 前端开发

- 使用 Vue 3 Composition API + `<script setup>` 语法
- 组件库选用 Naive UI，遵循其设计规范
- API 请求统一封装在 `src/api/` 目录下

---

## 致谢

| 项目/服务 | 说明 |
|---|---|
| [rembg](https://github.com/danielgatis/rembg) | 图像背景移除工具 |
| [DeepSeek](https://platform.deepseek.com/) | AI 视觉理解能力 |
| [通义万相](https://tongyi.aliyun.com/wanxiang) | AI 图像生成服务 |
| [Naive UI](https://www.naiveui.com/) | Vue 3 组件库 |
| [FastAPI](https://fastapi.tiangolo.com/) | 高性能 Python Web 框架 |
