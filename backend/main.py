"""
main.py — FastAPI 应用入口

启动命令：uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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

# CORS 中间件（前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（图片访问）
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(garments_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(recommend_router, prefix="/api")
app.include_router(outfits_router, prefix="/api")
app.include_router(wardrobes_router, prefix="/api")
app.include_router(packing_router, prefix="/api")
app.include_router(share_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
