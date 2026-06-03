# AnimeCloset — 动漫风AI穿搭助手

> 上传衣物 → 自动抠图+打标 → 衣橱管理 → 天气推荐 → 保存穿搭 → 日历展示

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | FastAPI + SQLAlchemy (async) + SQLite |
| 前端 | Vue 3 + Vite + Canvas (纸娃娃系统) |
| 抠图 | rembg (本地推理) |
| 多模态LLM | DeepSeek Vision |
| 文本LLM | DeepSeek Chat |
| 天气 | 和风天气 API |
| 存储 | 本地文件系统 (MVP) |

## 项目结构

```
animecloset/
├── backend/
│   ├── app/
│   │   ├── api/           # API 路由
│   │   │   ├── auth.py    # 认证接口
│   │   │   ├── garments.py# 衣物接口
│   │   │   ├── outfits.py # 穿搭接口
│   │   │   ├── recommend.py# 推荐接口
│   │   │   └── user.py    # 用户/捏人接口
│   │   ├── core/          # 核心配置
│   │   │   ├── config.py  # 环境变量/配置
│   │   │   ├── database.py# 数据库连接
│   │   │   └── security.py# JWT/密码
│   │   ├── models/        # SQLAlchemy ORM 模型
│   │   ├── schemas/       # Pydantic 请求/响应模型
│   │   ├── services/      # 业务逻辑
│   │   │   ├── bg_remove.py   # rembg 抠图
│   │   │   ├── llm_tag.py     # LLM 打标
│   │   │   ├── recommend.py   # 推荐算法
│   │   │   └── weather.py     # 天气查询
│   │   └── utils/         # 工具函数
│   ├── static/uploads/    # 图片存储
│   ├── avatars/           # 捏人素材
│   └── main.py            # FastAPI 入口
├── frontend/              # Vue 3 前端 (Phase 6)
├── docs/                  # 项目文档
└── README.md
```

## 开发计划

| Phase | 内容 | 状态 |
|-------|------|------|
| 0 | 项目初始化 | ✅ |
| 1 | 后端骨架 + 数据库 + 用户认证 | 🔄 |
| 2 | 衣物上传 + rembg抠图 + LLM打标 | ⏳ |
| 3 | 衣橱管理 CRUD | ⏳ |
| 4 | 推荐算法（天气+LLM+降级） | ⏳ |
| 5 | 穿搭保存 + 日历API | ⏳ |
| 6 | 前端页面 (Vue3) | ⏳ |
| 7 | 捏人系统 + Canvas纸娃娃 | ⏳ |
| 8 | 冷宫唤醒 + 统计 + 联调 | ⏳ |

## 快速开始

```bash
# 后端
conda activate animecloset
cd backend
pip install -r requirements.txt
python main.py

# 前端 (Phase 6)
cd frontend
npm install
npm run dev
```
