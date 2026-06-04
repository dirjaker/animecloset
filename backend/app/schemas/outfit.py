"""
schemas/outfit.py — 穿搭相关请求/响应模型
"""

from pydantic import BaseModel


class OutfitSave(BaseModel):
    """保存穿搭"""
    date: str                     # YYYY-MM-DD
    garment_ids: list[str | None] # 按顺序：上衣/下装/外套/鞋/配饰


class GarmentBrief(BaseModel):
    """衣物简要信息（用于穿搭展示）"""
    id: str
    category: str
    processed_url: str | None
    tags: dict = {}

    model_config = {"from_attributes": True}


class OutfitResponse(BaseModel):
    """穿搭记录响应"""
    id: str
    date: str
    garment_ids: list[str | None]
    garments: list[GarmentBrief]  # 展开的衣物详情
    weather: str | None
    temperature: int | None
    reason: str | None
    illustration_url: str | None = None

    model_config = {"from_attributes": True}


class CalendarDay(BaseModel):
    """日历中的一天"""
    date: str
    outfit: OutfitResponse | None = None


class CalendarResponse(BaseModel):
    """日历月份响应"""
    year: int
    month: int
    days: list[CalendarDay]
