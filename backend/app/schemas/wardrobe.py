"""
schemas/wardrobe.py — 衣橱相关请求/响应模型
"""

from pydantic import BaseModel


class WardrobeCreate(BaseModel):
    """创建衣橱"""
    name: str
    icon: str = "👔"


class WardrobeUpdate(BaseModel):
    """更新衣橱"""
    name: str | None = None
    icon: str | None = None
    sort_order: int | None = None


class WardrobeResponse(BaseModel):
    """衣橱响应"""
    id: str
    name: str
    icon: str
    sort_order: int
    garment_count: int = 0
    created_at: str

    model_config = {"from_attributes": True}


class AssignGarmentRequest(BaseModel):
    """将衣物分配到衣橱"""
    garment_id: str
