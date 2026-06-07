"""
schemas/packing.py — 打包清单相关请求/响应模型
"""

from pydantic import BaseModel


class PackingListCreate(BaseModel):
    """创建打包清单"""
    name: str
    destination: str | None = None
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD


class PackingListUpdate(BaseModel):
    """更新打包清单"""
    name: str | None = None
    destination: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    items: list[dict] | None = None
    notes: str | None = None


class PackingListResponse(BaseModel):
    """打包清单响应"""
    id: str
    name: str
    destination: str | None
    start_date: str
    end_date: str
    items: list[dict]
    notes: str | None
    created_at: str

    model_config = {"from_attributes": True}
