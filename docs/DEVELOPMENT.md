# 开发指南

## 1. 环境搭建

### 1.1 系统要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.12+ | 后端运行环境 |
| Node.js | 18+ | 前端构建工具 |
| Conda | 推荐 | Python 环境管理 |

### 1.2 快速搭建

```bash
# 克隆项目
git clone https://github.com/dirjaker/vestio.git
cd vestio

# 创建 Python 虚拟环境
conda create -n vestio python=3.12 -y
conda activate vestio

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend && npm install && cd ..

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入 API Key
```

### 1.3 环境变量

编辑 `backend/.env` 文件：

```env
# JWT 密钥（生产环境必须修改）
SECRET_KEY=your-secret-key-here

# 阿里云百炼 API Key（衣物打标 + AI 插画）
DASHSCOPE_API_KEY=sk-xxx

# DeepSeek API Key（穿搭推荐）
DEEPSEEK_API_KEY=sk-xxx

# 和风天气 API Key（天气查询，可选）
QWEATHER_API_KEY=xxx

# CORS 允许的源（逗号分隔）
CORS_ORIGINS=http://localhost,http://127.0.0.1
```

> **注意：** 不配置 AI API Key 时系统仍可正常使用，相关功能会降级运行：
> - 无 `DASHSCOPE_API_KEY`：衣物打标使用默认值，插画功能不可用
> - 无 `DEEPSEEK_API_KEY`：穿搭推荐使用随机降级方案
> - 无 `QWEATHER_API_KEY`：天气使用默认值（22°C 晴）

## 2. 开发模式

### 2.1 前后端分离开发

开发时建议前后端分别启动，方便热更新：

```bash
# 终端 1：启动后端
cd backend
python main.py
# 后端运行在 http://localhost:8000

# 终端 2：启动前端（Vite 开发服务器）
cd frontend
npm run dev
# 前端运行在 http://localhost:5173
```

Vite 开发服务器会自动代理 API 请求到后端。

### 2.2 生产模式

```bash
# 1. 构建前端
cd frontend && npm run build && cd ..
# 构建产物在 frontend/dist/

# 2. 启动后端（自动托管前端静态资源）
cd backend && python main.py
# 前后端统一访问 http://localhost:8000
```

后端通过 SPA 中间件自动处理前端路由：
- `/api/*` → FastAPI 路由
- `/static/*`, `/uploads/*` → 静态文件
- 其他路径 → 前端 `index.html`（SPA 路由回退）

## 3. 项目结构说明

### 3.1 后端结构

```
backend/
├── main.py              # 应用入口
│                        #   - FastAPI 实例化
│                        #   - SPA 中间件
│                        #   - CORS 配置
│                        #   - 路由注册
│                        #   - 静态文件挂载
│
├── app/
│   ├── api/             # API 路由层
│   │   ├── auth.py      #   注册/登录
│   │   ├── garments.py  #   衣物 CRUD（异步上传）
│   │   ├── outfits.py   #   穿搭记录 + 日历 + 插画
│   │   ├── recommend.py #   穿搭推荐入口
│   │   ├── wardrobes.py #   多衣橱管理
│   │   ├── packing.py   #   打包清单
│   │   ├── stats.py     #   数据统计（8 种统计维度）
│   │   ├── weather.py   #   天气查询
│   │   ├── ai.py        #   AI 助手（推荐/风格/识别）
│   │   ├── share.py     #   分享图片生成
│   │   └── user.py      #   用户信息 + 头像
│   │
│   ├── core/            # 核心模块
│   │   ├── config.py    #   配置管理（pydantic-settings + .env）
│   │   ├── database.py  #   SQLAlchemy 异步引擎 + 会话工厂
│   │   ├── security.py  #   JWT 生成/验证 + bcrypt + 依赖注入
│   │   └── categories.py#   统一衣物分类（枚举 + 别名映射）
│   │
│   ├── models/          # ORM 模型
│   │   ├── user.py      #   用户
│   │   ├── garment.py   #   衣物
│   │   ├── outfit.py    #   穿搭记录
│   │   ├── wardrobe.py  #   衣橱
│   │   ├── packing_list.py # 打包清单
│   │   └── recommend_log.py # 推荐日志
│   │
│   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── auth.py      #   认证相关
│   │   ├── garment.py   #   衣物相关
│   │   ├── outfit.py    #   穿搭相关
│   │   ├── recommend.py #   推荐相关
│   │   ├── wardrobe.py  #   衣橱相关
│   │   ├── packing.py   #   打包清单相关
│   │   └── user.py      #   用户相关
│   │
│   └── services/        # 业务逻辑层
│       ├── recommend.py #   推荐算法（LLM 调用 + 降级）
│       ├── llm_tag.py   #   视觉模型打标（通义千问 VL）
│       ├── bg_remove.py #   rembg 抠图
│       ├── weather.py   #   天气查询服务
│       ├── wanx.py      #   通义万相插画生成
│       └── task_manager.py # 异步任务管理器
```

### 3.2 前端结构

```
frontend/src/
├── main.js              # 入口
├── App.vue              # 根组件（含侧边栏布局）
├── themes.js            # 毛玻璃暗色主题配置
├── router/index.js      # Vue Router 路由定义
├── stores/              # Pinia 状态管理
│   ├── auth.js          #   认证状态（token/登录态）
│   └── theme.js         #   主题状态
├── api/index.js         # Axios 实例 + 拦截器 + API 函数
└── views/               # 页面组件
    ├── WardrobeView.vue #   衣橱主页（卡片布局 + 分类筛选）
    ├── RecommendView.vue#   穿搭推荐
    ├── CalendarView.vue #   穿搭日历
    ├── StatsView.vue    #   数据统计图表
    ├── AIView.vue       #   AI 助手（推荐/风格/识别）
    ├── PackingView.vue  #   打包清单
    ├── WeatherView.vue  #   天气查看
    ├── OutfitBuilder.vue#   搭配构建器
    ├── ProfileView.vue  #   个人中心
    └── LoginView.vue    #   登录/注册
```

## 4. 关键设计决策

### 4.1 衣物分类标准化

系统统一使用 5 个标准分类：**上衣、下装、外套、鞋、配饰**。

所有 LLM 返回的非标准分类名（如"裤子"、"裙子"、"鞋子"）都通过 `categories.py` 中的 `normalize_category()` 映射为标准值，避免数据不一致。

### 4.2 异步任务处理

衣物上传采用异步任务模式：
1. 上传接口立即返回 `task_id`
2. 后台 `asyncio.create_task` 执行抠图+打标
3. 前端轮询 `/api/garments/status/{task_id}`
4. CPU 密集任务（rembg）通过 `run_in_executor` 委托线程池

### 4.3 LLM 降级策略

推荐系统设计了多层降级：
1. **首选**：DeepSeek LLM 生成推荐 + 理由
2. **降级**：按类别随机选择 + 通用推荐理由
3. **温度筛选**：无匹配时放宽温度范围
4. **场合筛选**：不足 3 件时放宽场合条件

### 4.4 分类别名系统

LLM 输出的分类名不稳定（可能返回"裤子"、"鞋子"等），通过 `CATEGORY_ALIASES` 字典做模糊映射，确保数据一致性。

## 5. 常见开发任务

### 5.1 添加新的 API 接口

1. 在 `backend/app/api/` 中创建或编辑路由文件
2. 在 `backend/app/schemas/` 中定义请求/响应模型
3. 在 `backend/main.py` 中注册路由
4. 在 `frontend/src/api/index.js` 中添加前端调用函数

### 5.2 添加新的数据库表

1. 在 `backend/app/models/` 中创建 ORM 模型
2. 在 `backend/app/models/__init__.py` 中导入模型
3. 重启服务时自动创建表（`init_db()`）

> **注意：** 生产环境应使用 Alembic 进行数据库迁移。

### 5.3 添加新的前端页面

1. 在 `frontend/src/views/` 中创建 Vue 组件
2. 在 `frontend/src/router/index.js` 中添加路由
3. 如需认证，在路由 `meta` 中添加 `{ auth: true }`

## 6. 调试技巧

### 6.1 查看 SQL 日志

在 `backend/.env` 中设置 `DEBUG=True`，SQLAlchemy 会打印所有 SQL 语句。

### 6.2 查看推荐日志

推荐请求会记录到 `recommend_logs` 表，包含完整的 LLM 提示词和响应。

### 6.3 API 文档

启动服务后访问 http://localhost:8000/docs 使用 Swagger UI 测试所有接口。

## 7. 构建与部署

### 7.1 构建前端

```bash
cd frontend
npm run build
# 产物输出到 frontend/dist/
```

### 7.2 启动生产服务

```bash
cd backend
python main.py
# 或使用 uvicorn 直接启动
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 7.3 使用 Nginx 反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 8. 依赖说明

| 依赖 | 用途 |
|------|------|
| fastapi | Web 框架 |
| uvicorn | ASGI 服务器 |
| sqlalchemy + aiosqlite | 异步 ORM + SQLite 驱动 |
| pydantic + pydantic-settings | 数据验证 + 配置管理 |
| passlib + bcrypt | 密码哈希 |
| PyJWT | JWT 令牌 |
| httpx | 异步 HTTP 客户端 |
| rembg | AI 背景移除 |
| pillow | 图片处理 |
| scikit-image + numpy | 图像处理依赖（rembg 使用） |
| onnxruntime | ONNX 模型推理（rembg 使用） |
