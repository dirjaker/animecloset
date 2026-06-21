# API 接口文档

> 基础路径：`/api`
>
> 认证方式：Bearer Token（JWT）
>
> 在线文档：启动服务后访问 http://localhost:8000/docs

## 1. 认证接口

### 1.1 用户注册

```
POST /api/auth/register
```

**请求体：**
```json
{
  "email": "user@example.com",
  "nickname": "用户名",
  "password": "密码"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": "uuid-string",
  "nickname": "用户名"
}
```

**错误：**
- `400` — 该邮箱已注册

---

### 1.2 用户登录

```
POST /api/auth/login
```

**请求体：**
```json
{
  "email": "user@example.com",
  "password": "密码"
}
```

**响应：** 同注册接口

**错误：**
- `401` — 邮箱或密码错误

---

## 2. 衣物管理接口

> 🔒 所有接口需要认证

### 2.1 上传衣物图片

```
POST /api/garments/upload
Content-Type: multipart/form-data
```

**参数：**
- `file` (File) — 衣物图片（JPEG/PNG/WEBP，≤10MB）

**响应：**
```json
{
  "task_id": "uuid-string",
  "status": "pending"
}
```

**处理流程：** 异步执行抠图+打标，前端通过状态接口轮询。

---

### 2.2 查询任务状态

```
GET /api/garments/status/{task_id}
```

**响应：**
```json
{
  "task_id": "uuid-string",
  "status": "success",
  "garment_id": "uuid-string",
  "error": null
}
```

**状态值：**
| 状态 | 说明 |
|------|------|
| pending | 等待处理 |
| processing | 处理中 |
| removing_bg | 抠图中 |
| tagging | AI 打标中 |
| saving | 保存中 |
| success | 成功 |
| failed | 失败 |

---

### 2.3 获取衣物列表

```
GET /api/garments
```

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| category | string | - | 分类筛选（上衣/下装/外套/鞋/配饰） |
| wardrobe_id | string | - | 衣橱 ID 筛选 |
| is_favorite | bool | - | 收藏筛选 |
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量 |

**响应：**
```json
{
  "items": [
    {
      "id": "uuid",
      "original_url": "/static/uploads/xxx.jpg",
      "processed_url": "/static/uploads/xxx.png",
      "category": "上衣",
      "tags": {
        "color": "白色",
        "material": "棉",
        "style": ["休闲"],
        "season": ["春", "夏"],
        "occasion": ["日常"]
      },
      "temp_min": -30,
      "temp_max": 50,
      "wear_count": 5,
      "last_wear_date": "2024-06-15",
      "is_favorite": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

### 2.4 获取单件衣物详情

```
GET /api/garments/{garment_id}
```

---

### 2.5 更新衣物信息

```
PUT /api/garments/{garment_id}
```

**请求体：**
```json
{
  "category": "上衣",
  "tags": {
    "color": "蓝色",
    "material": "牛仔布",
    "style": ["复古"],
    "season": ["春", "秋"],
    "occasion": ["日常"]
  },
  "temp_min": 10,
  "temp_max": 30,
  "wardrobe_id": "wardrobe-uuid"
}
```

---

### 2.6 删除衣物

```
DELETE /api/garments/{garment_id}
```

---

### 2.7 切换收藏状态

```
PUT /api/garments/{garment_id}/favorite
```

**响应：**
```json
{
  "id": "uuid",
  "is_favorite": true
}
```

---

### 2.8 更新衣物生命周期

```
PUT /api/garments/{garment_id}/lifecycle
```

**查询参数：**
- `purchase_date` — 购买日期（YYYY-MM-DD）
- `purchase_price` — 购买价格（元）

---

## 3. 穿搭记录接口

### 3.1 保存穿搭

```
POST /api/outfits
```

**请求体：**
```json
{
  "date": "2024-06-15",
  "garment_ids": ["id1", "id2", "id3"]
}
```

**说明：** 同一天同一用户只保留一条记录（覆盖更新）。保存时自动更新衣物穿着次数。

---

### 3.2 获取穿搭日历

```
GET /api/outfits/calendar?month=2024-06
```

**响应：**
```json
{
  "year": 2024,
  "month": 6,
  "days": [
    {
      "date": "2024-06-01",
      "outfit": {
        "id": "uuid",
        "garment_ids": ["id1", "id2"],
        "garments": [...],
        "weather": "晴",
        "temperature": 28
      }
    },
    {
      "date": "2024-06-02",
      "outfit": null
    }
  ]
}
```

---

### 3.3 生成 AI 插画

```
POST /api/outfits/{outfit_id}/illustration
```

**响应：**
```json
{
  "status": "success",
  "illustration_url": "/static/illustrations/xxx.jpg"
}
```

---

## 4. 穿搭推荐接口

### 4.1 LLM 推荐

```
POST /api/recommend
```

**请求体：**
```json
{
  "date": "2024-06-15",
  "occasion": "工作",
  "extra_requirements": "需要正式一点"
}
```

**响应：**
```json
{
  "date": "2024-06-15",
  "weather": "晴",
  "temperature": 28,
  "selected_garments": [
    {
      "id": "uuid",
      "category": "上衣",
      "tags": { "color": "白色", "style": ["商务"] },
      "processed_url": "/static/uploads/xxx.png",
      "is_cold_palace": false
    }
  ],
  "reason": "今天晴朗28°C，适合穿白色衬衫搭配深色西裤...",
  "is_fallback": false
}
```

---

### 4.2 AI 智能推荐（天气+场合）

```
GET /api/ai/recommend?city=Beijing&occasion=日常
```

---

### 4.3 AI 风格分析

```
GET /api/ai/style-analysis
```

**响应：**
```json
{
  "total_garments": 42,
  "main_style": "休闲",
  "style_tags": [["休闲", 45.2], ["简约", 30.1], ...],
  "top_categories": [["上衣", 15], ["裤子", 10], ...],
  "top_colors": [["黑色", 8], ["白色", 6], ...],
  "suggestions": ["您的主要风格是「休闲」，舒适自然，日常百搭"]
}
```

---

## 5. 衣橱管理接口

### 5.1 获取所有衣橱

```
GET /api/wardrobes
```

### 5.2 创建衣橱

```
POST /api/wardrobes
```

**请求体：**
```json
{
  "name": "运动",
  "icon": "🏃"
}
```

### 5.3 更新衣橱

```
PUT /api/wardrobes/{wardrobe_id}
```

### 5.4 删除衣橱

```
DELETE /api/wardrobes/{wardrobe_id}
```

**说明：** 衣物自动移至默认衣橱，不允许删除最后一个衣橱。

### 5.5 分配衣物到衣橱

```
POST /api/wardrobes/{wardrobe_id}/garments
```

### 5.6 从衣橱移除衣物

```
DELETE /api/wardrobes/{wardrobe_id}/garments/{garment_id}
```

---

## 6. 打包清单接口

### 6.1 获取所有清单

```
GET /api/packing
```

### 6.2 创建清单

```
POST /api/packing
```

### 6.3 获取清单详情

```
GET /api/packing/{packing_id}
```

### 6.4 更新清单

```
PUT /api/packing/{packing_id}
```

### 6.5 删除清单

```
DELETE /api/packing/{packing_id}
```

### 6.6 AI 自动填充

```
POST /api/packing/{packing_id}/auto-fill
```

**说明：** 根据旅行天数自动从衣橱中按天分配衣物（上衣+下装+鞋）。

---

## 7. 统计接口

### 7.1 综合统计

```
GET /api/stats/summary
```

### 7.2 衣橱概览

```
GET /api/stats/wardrobe
```

### 7.3 冷宫衣物

```
GET /api/stats/cold-palace?days=30
```

### 7.4 穿着排行

```
GET /api/stats/wear-ranking?limit=10
```

### 7.5 月度统计

```
GET /api/stats/monthly
```

### 7.6 类别分布

```
GET /api/stats/category-distribution
```

### 7.7 每次穿着成本

```
GET /api/stats/cost-per-wear
```

### 7.8 季节分布

```
GET /api/stats/season-distribution
```

### 7.9 穿着趋势

```
GET /api/stats/wear-trend
```

**说明：** 最近 30 天每日穿着次数。

---

## 8. 天气接口

### 8.1 当前天气

```
GET /api/weather/current?city=Beijing
```

### 8.2 天气预报

```
GET /api/weather/forecast?city=Beijing&days=3
```

---

## 9. 用户接口

### 9.1 获取当前用户

```
GET /api/user/me
```

### 9.2 更新个人信息

```
PUT /api/user/me
```

### 9.3 修改密码

```
PUT /api/user/password
```

### 9.4 上传头像

```
POST /api/user/avatar/upload
Content-Type: multipart/form-data
```

---

## 10. 分享接口

### 10.1 生成分享图片

```
POST /api/share/outfit/{outfit_id}
```

**说明：** 将穿搭衣物拼接成一行拼图，底部叠加日期和天气文字，返回可访问的图片 URL。

---

## 11. 系统接口

### 11.1 健康检查

```
GET /health
```

**响应：**
```json
{ "status": "ok" }
```

---

## 错误码说明

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或令牌失效 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 500 | 服务器内部错误 |
