<div align="center">

<img src="assets/banner.svg" width="100%" alt="VESTIO - AI 智能穿衣镜系统">

<br>

### 🪞 智慧衣橱系统

[![Stars](https://img.shields.io/github/stars/dirjaker/vestio?style=flat-square&label=Stars&color=FFD700)](https://github.com/dirjaker/vestio/stargazers)
[![Forks](https://img.shields.io/github/forks/dirjaker/vestio?style=flat-square&label=Forks&color=4A90D9)](https://github.com/dirjaker/vestio/network/members)
[![Contributors](https://img.shields.io/github/contributors/dirjaker/vestio?style=flat-square&label=Contributors&color=8B4513)](https://github.com/dirjaker/vestio/graphs/contributors)
[![License](https://img.shields.io/github/license/dirjaker/vestio?style=flat-square&label=License&color=20B2AA)](https://github.com/dirjaker/vestio/blob/main/LICENSE)
[![Vue3](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)

</div>

---

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| 👗 **衣橱管理** | 上传、分类、搜索衣物，支持多衣橱管理和收藏功能 |
| ✂️ **AI 抠图** | 使用 rembg（u2net）一键去除衣物背景，自动裁剪为透明 PNG |
| 🎨 **智能打标** | 基于通义千问 VL（qwen-vl-plus）识别衣物颜色、材质、风格、季节 |
| 🤖 **智能搭配** | DeepSeek LLM 根据天气、场合、冷宫唤醒自动推荐穿搭方案 |
| 🌤️ **天气推荐** | 接入 wttr.in 实时天气，按温度/天气推荐适合的穿搭 |
| 📅 **穿搭日历** | 按日历记录每日穿搭，自动统计穿着次数 |
| 🎒 **打包清单** | 旅行打包清单管理，AI 自动按天分配衣物 |
| 📊 **数据统计** | 衣橱概览、穿着排行、冷宫衣物、每次穿着成本分析 |
| 🎭 **AI 插画** | 通义万相将衣物平铺图转换为 Q 版动漫风格穿搭插画 |
| 👤 **用户系统** | 注册/登录、头像上传、个人信息管理、每日穿搭提醒 |
| 🔗 **分享功能** | 一键生成穿搭分享图片，拼接衣物图+日期天气信息 |

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- Conda（推荐）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/dirjaker/vestio.git
cd vestio

# 2. 创建并激活虚拟环境
conda create -n vestio python=3.12 -y
conda activate vestio

# 3. 安装后端依赖
pip install -r requirements.txt

# 4. 安装前端依赖
cd frontend && npm install && cd ..

# 5. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 API Key

# 6. 构建前端
cd frontend && npm run build && cd ..

# 7. 启动服务（前后端统一端口）
cd backend && python main.py
```

### 环境变量配置

在 `backend/.env` 中配置以下变量：

| 变量 | 必填 | 说明 |
|------|------|------|
| `SECRET_KEY` | 否 | JWT 密钥（生产环境必须修改） |
| `DASHSCOPE_API_KEY` | 否 | 阿里云百炼 API Key（衣物打标 + AI 插画） |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek API Key（穿搭推荐） |
| `QWEATHER_API_KEY` | 否 | 和风天气 API Key（天气查询） |
| `CORS_ORIGINS` | 否 | CORS 允许的源（默认 `http://localhost,http://127.0.0.1`） |

### 访问地址

| 服务 | 地址 |
|------|------|
| 🌐 应用主页 | http://localhost:8000 |
| 📡 API 文档 | http://localhost:8000/docs |
| 📊 健康检查 | http://localhost:8000/health |

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Vue 3 + Naive UI)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ 衣橱管理 │ │ 穿搭推荐 │ │ 风格分析 │ │ 打包清单   │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ 穿搭日历 │ │ 数据统计 │ │ AI 插画  │ │ 天气查看   │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP API (JWT Auth)
┌────────────────────────┴────────────────────────────────┐
│                    后端 (FastAPI)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ 认证模块 │ │ 衣物管理 │ │ 穿搭引擎 │ │ 统计分析   │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ 天气服务 │ │ 抠图服务 │ │ 打标服务 │ │ 插画生成   │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
│                                                         │
│  ┌──────────┐ ┌──────────────────────────────────────┐  │
│  │ SQLite   │ │ AI 模型                               │  │
│  │ (异步)   │ │ 通义千问VL / DeepSeek / 通义万相     │  │
│  └──────────┘ └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
vestio/
├── backend/                # FastAPI 后端
│   ├── main.py             # 应用入口（含 SPA 中间件）
│   ├── .env.example        # 环境变量模板
│   └── app/
│       ├── api/            # API 路由
│       │   ├── auth.py     # 注册/登录
│       │   ├── garments.py # 衣物 CRUD
│       │   ├── outfits.py  # 穿搭记录 + 日历
│       │   ├── recommend.py# 穿搭推荐
│       │   ├── wardrobes.py# 多衣橱管理
│       │   ├── packing.py  # 打包清单
│       │   ├── stats.py    # 数据统计
│       │   ├── weather.py  # 天气查询
│       │   ├── ai.py       # AI 智能助手
│       │   ├── share.py    # 分享图片生成
│       │   └── user.py     # 用户信息
│       ├── core/           # 核心模块
│       │   ├── config.py   # 配置管理（pydantic-settings）
│       │   ├── database.py # SQLAlchemy 异步引擎
│       │   ├── security.py # JWT + bcrypt
│       │   └── categories.py# 统一衣物分类标准
│       ├── models/         # ORM 模型
│       │   ├── user.py     # 用户
│       │   ├── garment.py  # 衣物
│       │   ├── outfit.py   # 穿搭记录
│       │   ├── wardrobe.py # 衣橱
│       │   ├── packing_list.py # 打包清单
│       │   └── recommend_log.py # 推荐日志
│       ├── schemas/        # Pydantic 数据模型
│       └── services/       # 业务逻辑
│           ├── recommend.py # 推荐算法（LLM + 降级）
│           ├── llm_tag.py   # 视觉模型打标
│           ├── bg_remove.py # rembg 抠图
│           ├── weather.py   # 天气查询
│           ├── wanx.py      # 通义万相插画生成
│           └── task_manager.py # 异步任务管理
├── frontend/               # Vue 3 + Naive UI 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   │   ├── WardrobeView.vue   # 衣橱主页
│   │   │   ├── RecommendView.vue  # 穿搭推荐
│   │   │   ├── CalendarView.vue   # 穿搭日历
│   │   │   ├── StatsView.vue      # 数据统计
│   │   │   ├── AIView.vue         # AI 助手
│   │   │   ├── PackingView.vue    # 打包清单
│   │   │   ├── WeatherView.vue    # 天气查看
│   │   │   ├── OutfitBuilder.vue  # 搭配构建器
│   │   │   ├── ProfileView.vue    # 个人中心
│   │   │   └── LoginView.vue      # 登录/注册
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── api/            # Axios API 封装
│   │   ├── router/         # Vue Router
│   │   └── themes.js       # 毛玻璃暗色主题
│   └── public/
├── docs/                   # 项目文档
├── static/                 # 静态资源（上传/插画/分享图）
├── requirements.txt        # Python 依赖
└── LICENSE                 # MIT 许可证
```

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3.5、Naive UI、Pinia、Vue Router、Vite 8 |
| **后端** | FastAPI 0.136、SQLAlchemy 2.0（异步）、Pydantic 2.x |
| **数据库** | SQLite + aiosqlite |
| **认证** | JWT（PyJWT）+ bcrypt 密码哈希 |
| **AI 视觉** | 通义千问 VL（qwen-vl-plus）— 衣物图片分类打标 |
| **AI 文本** | DeepSeek Chat — 穿搭推荐理由生成 |
| **AI 图像** | 通义万相（wan2.7-image）— 动漫风格插画生成 |
| **抠图** | rembg（u2net，本地推理，无需 API） |
| **天气** | wttr.in（免费 API，无需 Key）/ 和风天气 |
| **图片处理** | Pillow + PIL |

## 📝 开发日志

- [x] 衣橱管理 CRUD + 多衣橱支持
- [x] AI 抠图（rembg u2net）
- [x] 通义千问 VL 图片分类打标
- [x] 天气 API 接入（wttr.in + 和风天气）
- [x] DeepSeek LLM 穿搭推荐 + 冷宫唤醒
- [x] 穿搭日历 + 穿着统计
- [x] 通义万相 AI 插画生成
- [x] 旅行打包清单 + AI 自动填充
- [x] 穿搭分享图片生成
- [x] 用户系统（注册/登录/头像/个人信息）
- [x] SPA 统一部署（前后端同端口）
- [x] 安全加固（CORS 限制、路径穿越防护）
- [ ] 移动端适配
- [ ] 社区分享功能

## 📚 文档

- [技术架构文档](docs/ARCHITECTURE.md)
- [API 接口文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)
- [更新日志](docs/CHANGELOG.md)

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

🔗 **GitHub**: [dirjaker/vestio](https://github.com/dirjaker/vestio)

⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！

</div>
