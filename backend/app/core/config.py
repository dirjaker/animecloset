"""
config.py — 应用配置管理

使用 pydantic-settings 从环境变量或 .env 文件加载配置。
敏感信息（API密钥）必须通过环境变量注入，不可硬编码。
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置项"""

    # ---- 应用基础 ----
    APP_NAME: str = "AnimeCloset"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ---- 数据库 ----
    DATABASE_URL: str = "sqlite+aiosqlite:///./animecloset.db"

    # ---- JWT 认证 ----
    SECRET_KEY: str = "dev-secret-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # ---- 文件存储 ----
    UPLOAD_DIR: str = str(Path(__file__).parent.parent.parent / "static" / "uploads")
    AVATAR_DIR: str = str(Path(__file__).parent.parent.parent / "avatars")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "webp"]

    # ---- DeepSeek API ----
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # ---- 和风天气 ----
    QWEATHER_API_KEY: str = ""
    QWEATHER_LOCATION_URL: str = "https://geoapi.qweather.com/v2/city/lookup"
    QWEATHER_WEATHER_URL: str = "https://devapi.qweather.com/v7/weather/now"

    # ---- 通义万相 ----
    DASHSCOPE_API_KEY: str = ""

    # ---- rembg 抠图 ----
    REMBG_MODEL: str = "u2net"  # u2net / u2netp / isnet-general-use

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# 全局单例
settings = Settings()
