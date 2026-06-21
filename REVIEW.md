# Vestio 代码审查与安全扫描报告

**项目：** Vestio — 虚拟穿衣镜（Vue3 + NaiveUI + FastAPI + SQLite）  
**扫描日期：** 2026-06-22  
**扫描范围：** 42 Python 文件 + 11 Vue 文件  
**审查工具：** 人工代码审查（静态分析）

---

## 🔴 严重（Critical）

### C-1：CORS 配置允许所有来源 + 凭证

**文件：** `backend/main.py` L81-87  
**风险等级：** 严重

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # ❌ 任意来源
    allow_credentials=True,     # ❌ 配合凭证
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**问题：** `allow_origins=["*"]` 搭配 `allow_credentials=True` 是高危配置。虽然现代浏览器会拦截 `*` + credentials 的组合，但部分旧浏览器和非浏览器客户端会接受，允许恶意站点携带用户 Cookie 发起跨域请求。

**建议：**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### C-2：硬编码 JWT 密钥

**文件：** `backend/app/core/config.py` L24  
**风险等级：** 严重

```python
SECRET_KEY: str = "dev-secret-change-in-production"
```

**问题：** 默认值是可预测的字符串。如果生产环境未正确设置 `.env`，攻击者可使用已知密钥伪造任意用户的 JWT 令牌，获得完全账户控制权。

**建议：**
- 移除默认值，改为 `SECRET_KEY: str`（必填），启动时校验长度 ≥ 32 字符
- 或使用 `secrets.token_urlsafe(64)` 在首次启动时自动生成并持久化

---

### C-3：SPA 中间件路径穿越漏洞

**文件：** `backend/main.py` L53-55  
**风险等级：** 严重

```python
file_path = FRONTEND_DIST / path.lstrip("/")
if file_path.is_file():
    return FileResponse(str(file_path))
```

**问题：** `path.lstrip("/")` 只移除前导斜杠，无法防御 `../` 路径穿越。请求 `GET /../../etc/passwd` → `lstrip("/")` 后变为 `../../etc/passwd` → `FRONTEND_DIST / "../../etc/passwd"` → 可读取服务器任意文件。

**建议：**
```python
file_path = (FRONTEND_DIST / path.lstrip("/")).resolve()
if not str(file_path).startswith(str(FRONTEND_DIST.resolve())):
    return await call_next(request)
if file_path.is_file():
    return FileResponse(str(file_path))
```

---

## 🟠 高危（High）

### H-1：天气接口 SSRF（服务端请求伪造）

**文件：** `backend/app/api/weather.py` L25, L67；`backend/app/api/ai.py` L149  
**风险等级：** 高

```python
resp = await client.get(f"https://wttr.in/{city}?format=j1", ...)
```

**问题：** `city` 参数直接拼入 URL，未经校验。攻击者可注入路径（如 `../../internal-api`）或特殊字符，可能访问内网服务或触发意外行为。

**建议：**
- 校验 `city` 只含字母、数字、空格、连字符
- 使用 `urllib.parse.quote(city, safe="")` 编码
- 限制最大长度（如 50 字符）

---

### H-2：任务状态接口缺少身份验证

**文件：** `backend/app/api/garments.py` L77-93  
**风险等级：** 高

```python
@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task(task_id: str):  # ❌ 无 user 依赖
```

**问题：** `task_id` 是 UUID，但接口无需认证即可查询。任何知道 task_id 的人可以：
1. 获取衣物处理状态和 `garment_id`
2. 通过枚举 UUID 探测系统活动

**建议：** 添加 `user: User = Depends(get_current_user)` 并校验 task 归属。

---

### H-3：内存任务存储无清理机制

**文件：** `backend/app/services/task_manager.py` L34  
**风险等级：** 高

```python
_tasks: dict[str, dict] = {}  # 只增不减
```

**问题：** 任务完成后永不删除，长时间运行会导致内存泄漏。同时进程重启后所有任务丢失。

**建议：**
- 定时清理已完成超过 1 小时的任务
- 生产环境改用 Redis 或数据库存储任务状态

---

### H-4：头像上传扩展名校验不严

**文件：** `backend/app/api/user.py` L126-127  
**风险等级：** 高

```python
ext = filename_base.split(".")[-1] if "." in filename_base else "jpg"
filename = f"{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
```

**问题：** 
1. 仅靠 `content_type` 校验文件类型，客户端可伪造
2. 扩展名未校验白名单，可能保存为 `.php`、`.html`、`.svg` 等危险类型
3. `ai.py` L355 的 `identify-garment` 端点存在同样问题

**建议：**
```python
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ext = filename_base.split(".")[-1].lower()
if ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail="不支持的文件格式")
```

---

## 🟡 中等（Medium）

### M-1：异常信息泄露

**文件：** `backend/app/api/outfits.py` L274  
**风险等级：** 中

```python
raise HTTPException(status_code=500, detail=f"插画生成失败: {str(e)}")
```

**问题：** 将内部异常信息直接返回给客户端，可能泄露文件路径、库版本等敏感信息。

**建议：** 返回通用错误信息，详细错误记录到日志：
```python
logger.error(f"插画生成失败: {e}")
raise HTTPException(status_code=500, detail="插画生成失败，请稍后重试")
```

---

### M-2：JWT 令牌有效期过长且无法撤销

**文件：** `backend/app/core/config.py` L25  
**风险等级：** 中

```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
```

**问题：** 令牌一旦签发，在 7 天内无法撤销。用户修改密码后旧令牌仍有效。缺少 refresh token 机制。

**建议：**
- 缩短 access token 有效期至 15-30 分钟
- 实现 refresh token 机制
- 修改密码时加入 token 版本号校验

---

### M-3：数据库引擎缺少连接池限制

**文件：** `backend/app/core/database.py` L14-17  
**风险等级：** 中

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)
```

**问题：** 未配置 `pool_size`、`max_overflow` 等参数。虽然 SQLite 限制了并发写入，但在高并发场景下可能耗尽文件描述符。

**建议：**
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)
```

---

### M-4：端点中直接调用 `db.commit()`

**文件：** `backend/app/api/garments.py` L217  
**风险等级：** 中

```python
garment.is_favorite = not garment.is_favorite
await db.commit()  # ❌ 绕过 get_db 的统一事务管理
```

**问题：** `get_db` 依赖已提供统一的 commit/rollback 语义。端点内直接 `commit()` 会导致：1) 双重 commit；2) 异常时无法正确 rollback。

**建议：** 改为 `await db.flush()`，让 `get_db` 统一管理事务。

---

### M-5：前端 JWT 存储方式需确认

**文件：** `frontend/src/views/LoginView.vue` L89  
**风险等级：** 中

```javascript
authStore.setAuth(data.access_token, { id: data.user_id, nickname: data.nickname })
```

**问题：** 需确认 `authStore` 将 token 存储在哪里。如果使用 `localStorage`，容易受到 XSS 攻击窃取；如果使用 `httpOnly Cookie`，需确保设置了 `SameSite` 和 `Secure` 属性。

**建议：** 推荐使用 `httpOnly` + `Secure` + `SameSite=Strict` Cookie 存储认证令牌。

---

### M-6：注册接口缺少频率限制

**文件：** `backend/app/api/auth.py` L20-56  
**风险等级：** 中

**问题：** 注册和登录接口均无速率限制，攻击者可进行：
- 暴力破解密码
- 批量注册垃圾账户
- 拒绝服务攻击

**建议：** 使用 `slowapi` 或 Nginx 层面限制：
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/register")
@limiter.limit("5/minute")
async def register(...): ...
```

---

## 🟢 低危（Low）

### L-1：DEBUG 模式默认开启

**文件：** `backend/app/core/config.py` L18  
**风险等级：** 低

```python
DEBUG: bool = True
```

**问题：** 生产环境如果忘记关闭，`echo=settings.DEBUG` 会将所有 SQL 语句打印到日志，可能暴露数据结构。

**建议：** 生产环境 `.env` 中显式设置 `DEBUG=false`。

---

### L-2：garments 路径构造使用相对路径

**文件：** `backend/main.py` L95-97  
**风险等级：** 低

```python
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
```

**问题：** `uploads_dir` 与 `settings.UPLOAD_DIR` 指向不同位置，可能导致文件存储混乱。上传的衣物图片存入 `settings.UPLOAD_DIR`（`static/uploads`），但 `/uploads` 挂载的是 `backend/uploads` 目录。

**建议：** 统一使用 `settings.UPLOAD_DIR` 作为唯一的文件存储路径。

---

### L-3：`asyncio.get_event_loop()` 使用已弃用 API

**文件：** `backend/app/services/task_manager.py` L78, L91  
**风险等级：** 低

```python
loop = asyncio.get_event_loop()
file_bytes = await loop.run_in_executor(None, resize_image, file_bytes, 1024)
```

**问题：** Python 3.10+ 中 `get_event_loop()` 在无运行循环时会发出 DeprecationWarning。

**建议：** 使用 `asyncio.get_running_loop()` 或直接使用 `asyncio.to_thread()`（Python 3.9+）。

---

## ✅ 良好实践

| 类别 | 评价 |
|------|------|
| **SQL 注入防护** | ✅ 全量使用 SQLAlchemy ORM 参数化查询，未发现原始 SQL 拼接 |
| **密码存储** | ✅ 使用 bcrypt 哈希，`passlib` 配置正确 |
| **JWT 实现** | ✅ 使用 HS256 算法，payload 包含 `exp`/`iat`/`sub` 标准字段 |
| **XSS 防护** | ✅ Vue3 模板默认转义 HTML，未发现 `v-html` 使用 |
| **数据隔离** | ✅ 所有数据查询均带 `user_id` 过滤，无法越权访问他人数据 |
| **输入校验** | ✅ 使用 Pydantic schema 进行请求体校验 |
| **文件大小限制** | ✅ 上传接口均限制 10MB / 5MB |
| **文件类型校验** | ⚠️ 基于 `content_type`（可伪造），需补充文件魔数校验 |

---

## 📊 评分

| 维度 | 得分 | 说明 |
|------|------|------|
| SQL 注入防护 | **9/10** | ORM 使用规范，无原始 SQL |
| 文件上传安全 | **5/10** | 缺少扩展名白名单和魔数校验 |
| API 认证安全 | **6/10** | JWT 实现正确，但令牌过长、无撤销机制、部分接口漏加认证 |
| 前端 XSS 防护 | **8/10** | Vue3 默认安全，无 `v-html` |
| CORS 配置 | **3/10** | 通配符 + 凭证，高危配置 |
| 错误处理 | **5/10** | 异常信息泄露，部分异常被静默吞没 |
| 整体架构 | **7/10** | 分层清晰，依赖注入规范 |

### **综合评分：6.5 / 10**

> 总体代码质量良好，架构规范。主要风险集中在部署配置层面（CORS、密钥、路径校验）。修复 C-1 ~ C-3 三个严重项后可提升至 **8.0+**。

---

## 🔧 修复优先级

| 优先级 | 编号 | 问题 | 预估工时 |
|--------|------|------|----------|
| P0 | C-1 | CORS 通配符配置 | 0.5h |
| P0 | C-2 | 硬编码 JWT 密钥 | 0.5h |
| P0 | C-3 | SPA 路径穿越 | 1h |
| P1 | H-1 | 天气接口 SSRF | 0.5h |
| P1 | H-2 | 任务状态接口无认证 | 0.5h |
| P1 | H-4 | 文件扩展名白名单 | 1h |
| P2 | M-2 | JWT 刷新机制 | 4h |
| P2 | M-6 | 接口频率限制 | 2h |
| P3 | 其余 | 低危项 | 2h |

**总预估工时：** 约 12 小时
