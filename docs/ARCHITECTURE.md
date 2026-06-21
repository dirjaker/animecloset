# 技术架构文档

## 1. 系统概述

Vestio（智慧衣橱系统）是一个基于 AI 的个人穿搭管理 Web 应用。系统采用前后端分离架构，通过 SPA 模式统一部署到同一端口，后端提供 RESTful API，前端通过 Vue 3 构建单页应用。

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      浏览器                              │
│                 Vue 3 SPA (Naive UI)                     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (JSON)
                       ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI 应用服务器 (:8000)                  │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  中间件层                                           │ │
│  │  ├─ SPA Middleware (前端静态资源 + 路由回退)        │ │
│  │  ├─ CORS Middleware (跨域访问控制)                  │ │
│  │  └─ JWT Auth (Bearer Token 认证)                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  API 路由层 (/api/*)                               │ │
│  │  ├─ auth      注册 / 登录                          │ │
│  │  ├─ garments  衣物 CRUD + 异步上传                 │ │
│  │  ├─ outfits   穿搭记录 / 日历 / AI 插画            │ │
│  │  ├─ recommend LLM 穿搭推荐                         │ │
│  │  ├─ wardrobes 多衣橱管理                           │ │
│  │  ├─ packing   打包清单 + AI 填充                    │ │
│  │  ├─ stats     统计分析                             │ │
│  │  ├─ weather   天气查询                             │ │
│  │  ├─ ai        AI 助手（推荐/风格分析/识别）        │ │
│  │  ├─ share     分享图片生成                         │ │
│  │  └─ user      用户信息管理                         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  服务层                                             │ │
│  │  ├─ TaskManager   异步任务管理（抠图+打标）        │ │
│  │  ├─ BgRemove      rembg 本地抠图                   │ │
│  │  ├─ LLMTag        通义千问 VL 图片分类             │ │
│  │  ├─ Recommend      DeepSeek 推荐算法               │ │
│  │  ├─ Weather        wttr.in / 和风天气              │ │
│  │  └─ WanX           通义万相插画生成                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  数据层                                             │ │
│  │  ├─ SQLAlchemy 2.0 (异步模式 + aiosqlite)          │ │
│  │  ├─ SQLite 数据库 (vestio.db)                      │ │
│  │  └─ 文件存储 (static/uploads/)                     │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 3. 数据库设计

### ER 关系图

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│  users   │────<│ garments │     │   wardrobes  │
│          │     │          │>────│              │
│ id (PK)  │     │ id (PK)  │     │ id (PK)      │
│ email    │     │ user_id  │     │ user_id      │
│ nickname │     │ wardrobe │     │ name         │
│ password │     │ category │     │ icon         │
│ avatar   │     │ tags(JSON)│    │ sort_order   │
│ ...      │     │ ...      │     └──────────────┘
└──────────┘     └──────────┘
     │                                    
     │          ┌──────────┐     ┌──────────────┐
     │────<     │ outfits  │     │packing_lists │
     │          │          │     │              │
     │          │ id (PK)  │     │ id (PK)      │
     │          │ user_id  │     │ user_id      │
     │          │ date     │     │ name         │
     │          │ garment_ │     │ destination  │
     │          │  ids(JSON)│    │ dates        │
     │          │ weather  │     │ items(JSON)  │
     │          │ ...      │     └──────────────┘
     │          └──────────┘
     │
     │────<  recommend_logs
```

### 表结构

#### users — 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | UUID 主键 |
| email | VARCHAR(255) UNIQUE | 邮箱（登录账号） |
| nickname | VARCHAR(100) | 昵称 |
| hashed_password | VARCHAR(255) | bcrypt 密码哈希 |
| gender | VARCHAR(10) | 性别（male/female/other） |
| avatar_url | VARCHAR(500) | 头像 URL |
| avatar_config | TEXT | 捏人配置 JSON |
| daily_reminder | BOOLEAN | 是否开启每日提醒 |
| reminder_time | VARCHAR(5) | 提醒时间（HH:MM） |
| created_at | DATETIME | 创建时间 |

#### garments — 衣物表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | UUID 主键 |
| user_id | VARCHAR(36) FK | 所属用户 |
| wardrobe_id | VARCHAR(36) FK | 所属衣橱（可选） |
| original_url | VARCHAR(500) | 原始图片路径 |
| processed_url | VARCHAR(500) | 抠图后透明 PNG 路径 |
| category | VARCHAR(20) | 分类（上衣/下装/外套/鞋/配饰） |
| tags | TEXT | JSON 标签（颜色/材质/风格/季节/场合） |
| temp_min | INTEGER | 适用最低温度 |
| temp_max | INTEGER | 适用最高温度 |
| wear_count | INTEGER | 穿着次数 |
| last_wear_date | DATE | 最后穿着日期 |
| is_favorite | BOOLEAN | 是否收藏 |
| purchase_date | DATE | 购买日期 |
| purchase_price | FLOAT | 购买价格（元） |
| created_at | DATETIME | 创建时间 |

**tags JSON 结构：**
```json
{
  "color": "白色",
  "material": "棉",
  "style": ["休闲", "简约"],
  "season": ["春", "夏"],
  "occasion": ["日常", "工作"]
}
```

#### outfits — 穿搭记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | UUID 主键 |
| user_id | VARCHAR(36) FK | 所属用户 |
| date | DATE UNIQUE(user_id, date) | 穿搭日期 |
| garment_ids | TEXT | 衣物 ID 列表（JSON 数组） |
| weather | VARCHAR(50) | 当日天气 |
| temperature | INTEGER | 当日温度 |
| reason | TEXT | 推荐理由 |
| illustration_url | VARCHAR(500) | AI 插画路径 |
| created_at | DATETIME | 创建时间 |

#### wardrobes — 衣橱表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | UUID 主键 |
| user_id | VARCHAR(36) FK | 所属用户 |
| name | VARCHAR(50) | 衣橱名称 |
| icon | VARCHAR(50) | 图标（emoji） |
| sort_order | INTEGER | 排序顺序 |
| created_at | DATETIME | 创建时间 |

#### packing_lists — 打包清单表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | UUID 主键 |
| user_id | VARCHAR(36) FK | 所属用户 |
| name | VARCHAR(100) | 清单名称 |
| destination | VARCHAR(100) | 目的地 |
| start_date | DATE | 开始日期 |
| end_date | DATE | 结束日期 |
| items | TEXT | 行程安排（JSON） |
| notes | TEXT | 备注 |
| created_at | DATETIME | 创建时间 |

#### recommend_logs — 推荐日志表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | UUID 主键 |
| user_id | VARCHAR(36) FK | 所属用户 |
| request_context | TEXT | 请求上下文 JSON |
| prompt | TEXT | 发送给 LLM 的提示词 |
| llm_response | TEXT | LLM 原始响应 |
| selected_ids | TEXT | 用户最终选择 |
| created_at | DATETIME | 创建时间 |

## 4. 核心流程

### 4.1 衣物上传处理流程

```
用户上传图片
    │
    ▼
校验格式 (JPEG/PNG/WEBP) + 大小 (≤10MB)
    │
    ▼
创建异步任务 → 返回 task_id
    │
    ▼ (后台 asyncio)
图片缩放 (≤1024px)
    │
    ▼
保存原图 → /static/uploads/{uuid}.jpg
    │
    ▼
rembg 抠图 (u2net CPU 推理，约 3-8s)
    │
    ▼
保存透明 PNG → /static/uploads/{uuid}.png
    │
    ▼
通义千问 VL 打标 (qwen-vl-plus)
    │
    ▼
保存到数据库 (Garment 表)
    │
    ▼
前端轮询 /api/garments/status/{task_id}
状态流: pending → processing → removing_bg → tagging → saving → success
```

### 4.2 穿搭推荐流程

```
用户请求推荐（日期 + 场合 + 城市）
    │
    ▼
获取天气数据（wttr.in / 和风天气）
    │
    ▼
查询用户衣橱所有衣物
    │
    ▼
按温度范围筛选衣物
    │
    ▼
按场合标签筛选（不足 3 件则放宽）
    │
    ▼
标记冷宫衣物（30 天未穿）
    │
    ▼
按类别分组（上衣/下装/外套/鞋/配饰）
    │
    ▼
调用 DeepSeek LLM 生成推荐组合
    │
    ▼ (降级策略)
LLM 不可用 → 随机选择 + 基础搭配理由
```

### 4.3 AI 插画生成流程

```
用户点击"生成插画"
    │
    ▼
获取穿搭记录中的衣物图片
    │
    ▼
拼合平铺参考图 (Pillow, 1024×1024)
    │
    ▼
调用通义万相 API (wan2.7-image)
    │
    ▼
轮询任务状态 (最长 120s)
    │
    ▼
下载生成图片 → 保存到本地
    │
    ▼
更新穿搭记录 illustration_url
```

## 5. 安全设计

### 5.1 认证机制

- **密码存储**：bcrypt 哈希（passlib）
- **令牌**：JWT（HS256），有效期 7 天
- **传输**：Bearer Token in Authorization Header

### 5.2 安全措施

- CORS 限制为本地访问源
- 文件上传格式和大小校验
- SPA 中间件路径穿越防护（`os.path.realpath` 校验）
- SQL 注入防护（SQLAlchemy ORM 参数化查询）
- 用户数据隔离（所有查询都带 `user_id` 条件）

## 6. AI 模型分工

| 模型 | 用途 | 提供商 |
|------|------|--------|
| qwen-vl-plus | 衣物图片分类打标 | 阿里云百炼 |
| deepseek-chat | 穿搭推荐理由生成 | DeepSeek |
| wan2.7-image | 动漫风格插画生成 | 阿里云百炼 |
| u2net | 背景移除（抠图） | 本地推理 (rembg) |

## 7. 性能优化

- **异步架构**：FastAPI + SQLAlchemy async + aiosqlite，非阻塞 I/O
- **异步任务**：衣物上传采用任务队列模式，前端轮询状态，避免请求超时
- **CPU 密集任务**：rembg 抠图通过 `run_in_executor` 委托到线程池
- **N+1 查询优化**：衣橱列表使用子查询一次性获取衣物数量
- **图片预处理**：上传前等比缩放至 ≤1024px，减少处理时间
- **SPA 部署**：前端构建后由后端统一托管，减少部署复杂度
