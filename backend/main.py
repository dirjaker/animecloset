"""
main.py — FastAPI 应用入口

启动命令：uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.core.database import init_db

# 导入所有模型（必须在 init_db 之前，确保表被注册）
import app.models  # noqa: F401

# 导入路由
from app.api.auth import router as auth_router
from app.api.garments import router as garments_router
from app.api.user import router as user_router
from app.api.stats import router as stats_router
from app.api.recommend import router as recommend_router
from app.api.outfits import router as outfits_router
from app.api.wardrobes import router as wardrobes_router
from app.api.packing import router as packing_router
from app.api.share import router as share_router
from app.api.weather import router as weather_router
from app.api.ai import router as ai_router

# 前端 dist 目录
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


class SPAMiddleware(BaseHTTPMiddleware):
    """SPA 中间件：非 API 请求返回前端 index.html"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # API、health、docs、后端静态资源 → 正常处理
        if (path.startswith("/api") or path.startswith("/health") or
                path.startswith("/docs") or path.startswith("/openapi") or
                path.startswith("/static") or path.startswith("/uploads")):
            return await call_next(request)

        # 前端 dist 静态文件（assets、favicon 等）
        if FRONTEND_DIST.exists():
            file_path = FRONTEND_DIST / path.lstrip("/")
            if file_path.is_file():
                return FileResponse(str(file_path))
            # 非 API 路径 → SPA index.html
            return FileResponse(str(FRONTEND_DIST / "index.html"))

        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    print("✅ 数据库初始化完成")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# SPA 中间件（必须在 CORS 之前）
if FRONTEND_DIST.exists():
    app.add_middleware(SPAMiddleware)

# CORS 中间件（前端跨域）
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（图片访问）
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 上传文件静态服务
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 注册 API 路由
app.include_router(auth_router, prefix="/api")
app.include_router(garments_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(recommend_router, prefix="/api")
app.include_router(outfits_router, prefix="/api")
app.include_router(wardrobes_router, prefix="/api")
app.include_router(packing_router, prefix="/api")
app.include_router(share_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(ai_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
