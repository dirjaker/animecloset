"""
services/weather.py — 天气查询服务

功能：
1. 根据城市名查询实时天气
2. 使用和风天气 API
3. 降级策略：API 不可用时返回默认值
"""

import logging
import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)


async def get_weather(city: str = "北京") -> dict:
    """
    查询天气

    Args:
        city: 城市名（中文）

    Returns:
        {"weather": "晴", "temperature": 25, "city": "北京"}
    """
    if not settings.QWEATHER_API_KEY:
        logger.warning("未配置 QWEATHER_API_KEY，使用默认天气")
        return _default_weather()

    try:
        # 1. 先查城市 ID
        location_id = await _lookup_city(city)
        if not location_id:
            return _default_weather()

        # 2. 查实时天气
        return await _get_realtime(location_id, city)

    except Exception as e:
        logger.error(f"天气查询失败: {e}")
        return _default_weather()


async def _lookup_city(city: str) -> str | None:
    """查询城市 ID"""
    url = settings.QWEATHER_LOCATION_URL
    params = {"location": city, "key": settings.QWEATHER_API_KEY}

    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        locations = data.get("location", [])
        if locations:
            return locations[0].get("id")
    return None


async def _get_realtime(location_id: str, city: str) -> dict:
    """获取实时天气"""
    url = settings.QWEATHER_WEATHER_URL
    params = {"location": location_id, "key": settings.QWEATHER_API_KEY}

    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        now = data.get("now", {})

        return {
            "weather": now.get("text", "未知"),
            "temperature": int(now.get("temp", 20)),
            "city": city,
        }


def _default_weather() -> dict:
    """默认天气（降级方案）"""
    return {"weather": "晴", "temperature": 22, "city": "未知"}
