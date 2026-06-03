# 🎫 AnimeCloset — 动漫风AI穿搭助手

> 上传衣物 → 自动抠图+打标 → 衣橱管理 → 天气推荐 → 保存穿搭 → 日历展示

## 功能特性

- 📸 **智能打标** — 上传衣物照片，rembg 本地抠图 + DeepSeek Vision 自动识别属性
- 👗 **衣橱管理** — 按类别筛选、编辑标签、穿着统计
- 🌤️ **天气推荐** — 根据天气+场合+温度智能推荐穿搭
- 📅 **日历展示** — 月视图展示每日穿搭，Canvas 纸娃娃渲染
- 🎨 **捏人系统** — 自定义发型/肤色/眼睛，实时预览
- ❄️ **冷宫唤醒** — 自动标记30天未穿衣物，推荐时优先考虑

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | FastAPI + SQLAlchemy (async) + SQLite |
| 前端 | Vue 3 + Vite + Canvas 纸娃娃 |
| 抠图 | rembg (本地推理, u2net) |
| LLM | DeepSeek Chat/Vision |
| 天气 | 和风天气 API |

## 项目结构

```
animecloset/
├── backend/
│   ├── app/
│   │   ├── api/           # 6个API模块 (auth/garments/outfits/recommend/stats/user)
│   │   ├── core/          # config/database/security
│   │   ├── models/        # 4张ORM表
│   │   ├── schemas/       # Pydantic模型
│   │   └── services/      # 5个服务 (bg_remove/llm_tag/recommend/weather/task_manager)
│   └── main.py
├── frontend/
│   └── src/
│       ├── api/           # Axios客户端
│       ├── components/    # AvatarCanvas纸娃娃组件
│       ├── views/         # 5个页面 (Login/Wardrobe/Recommend/Calendar/Profile)
│       ├── router/        # Vue Router + 路由守卫
│       └── utils/         # 颜色映射工具
└── docs/
```

## 快速开始

```bash
# 后端
conda activate animecloset
cd backend
pip install -r requirements.txt
python main.py
# → http://localhost:8000 (API文档: /docs)

# 前端
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| POST | /api/garments/upload | 上传衣物（异步抠图+打标） |
| GET | /api/garments | 衣橱列表 |
| PUT | /api/garments/{id} | 更新衣物 |
| DELETE | /api/garments/{id} | 删除衣物 |
| POST | /api/recommend | 穿搭推荐 |
| POST | /api/outfits | 保存穿搭 |
| GET | /api/outfits/calendar | 日历数据 |
| GET | /api/stats/wardrobe | 衣橱统计 |
| GET | /api/stats/cold-palace | 冷宫衣物 |
| GET | /api/stats/wear-ranking | 穿着排行 |
| GET/PUT | /api/user/avatar | 捏人配置 |

## 开发日志

| Phase | 内容 | 提交 |
|-------|------|------|
| 0 | 项目初始化 | ✅ |
| 1 | 后端骨架 + JWT认证 | ✅ |
| 2 | 衣物上传 + rembg抠图 + LLM打标 | ✅ |
| 3 | 衣橱管理 + 统计API | ✅ |
| 4 | 推荐算法（天气+LLM+降级） | ✅ |
| 5 | 穿搭保存 + 日历API | ✅ |
| 6 | Vue3前端（5个页面） | ✅ |
| 7 | 捏人系统 + Canvas纸娃娃 | ✅ |
| 8 | 冷宫唤醒 + 统计面板 | ✅ |
