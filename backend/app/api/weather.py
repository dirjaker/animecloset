"""
api/weather.py — 天气预报接口

使用 wttr.in 免费 API 获取天气信息，无需 API Key。
"""

import httpx
from fastapi import APIRouter, Depends, Query

from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/weather", tags=["天气"])


@router.get("/current")
async def get_current_weather(
    city: str = Query("Beijing", description="城市名称"),
    user: User = Depends(get_current_user),
):
    """获取当前天气"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://wttr.in/{city}?format=j1",
                headers={"Accept-Language": "zh-CN"},
            )
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_condition", [{}])[0]
                return {
                    "city": city,
                    "temp_c": current.get("temp_C", ""),
                    "temp_f": current.get("temp_F", ""),
                    "feels_like_c": current.get("FeelsLikeC", ""),
                    "humidity": current.get("humidity", ""),
                    "wind_speed_kmph": current.get("windspeedKmph", ""),
                    "wind_dir": current.get("winddir16Point", ""),
                    "weather_desc": current.get("lang_zh", [{}])[0].get("value", current.get("weatherDesc", [{}])[0].get("value", "")),
                    "weather_code": current.get("weatherCode", ""),
                    "visibility": current.get("visibility", ""),
                    "uv_index": current.get("uvIndex", ""),
                    "cloud_cover": current.get("cloudcover", ""),
                    "observation_time": current.get("observation_time", ""),
                }
    except Exception:
        pass
    
    return {
        "city": city,
        "temp_c": "N/A",
        "weather_desc": "无法获取天气数据",
        "error": True,
    }


@router.get("/forecast")
async def get_weather_forecast(
    city: str = Query("Beijing", description="城市名称"),
    days: int = Query(3, ge=1, le=3, description="预报天数"),
    user: User = Depends(get_current_user),
):
    """获取天气预报（最多3天）"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://wttr.in/{city}?format=j1",
                headers={"Accept-Language": "zh-CN"},
            )
            if resp.status_code == 200:
                data = resp.json()
                forecasts = []
                for day in data.get("weather", [])[:days]:
                    hourly = []
                    for h in day.get("hourly", []):
                        hourly.append({
                            "time": h.get("time", ""),
                            "temp_c": h.get("tempC", ""),
                            "weather_desc": h.get("lang_zh", [{}])[0].get("value", h.get("weatherDesc", [{}])[0].get("value", "")),
                            "weather_code": h.get("weatherCode", ""),
                            "chance_of_rain": h.get("chanceofrain", ""),
                            "humidity": h.get("humidity", ""),
                            "wind_speed_kmph": h.get("windspeedKmph", ""),
                        })
                    
                    forecasts.append({
                        "date": day.get("date", ""),
                        "max_temp_c": day.get("maxtempC", ""),
                        "min_temp_c": day.get("mintempC", ""),
                        "avg_temp_c": day.get("avgtempC", ""),
                        "sunrise": day.get("astronomy", [{}])[0].get("sunrise", ""),
                        "sunset": day.get("astronomy", [{}])[0].get("sunset", ""),
                        "hourly": hourly,
                    })
                
                return {
                    "city": city,
                    "forecasts": forecasts,
                }
    except Exception:
        pass
    
    return {
        "city": city,
        "forecasts": [],
        "error": True,
    }
