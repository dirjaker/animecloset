"""
schemas/garment.py — 衣物相关请求/响应模型
"""

from pydantic import BaseModel


class GarmentTags(BaseModel):
    """衣物标签结构"""
    color: str = ""           # 主颜色
    material: str = ""        # 材质
    style: list[str] = []     # 风格（休闲/商务/运动等）
    season: list[str] = []    # 季节（春/夏/秋/冬）
    occasion: list[str] = []  # 场合（工作/日常/聚会/户外）


class GarmentUpdate(BaseModel):
    """更新衣物信息"""
    category: str | None = None
    tags: GarmentTags | None = None
    temp_min: int | None = None
    temp_max: int | None = None


class GarmentResponse(BaseModel):
    """衣物详情响应"""
    id: str
    original_url: str
    processed_url: str | None
    category: str
    tags: GarmentTags
    temp_min: int
    temp_max: int
    wear_count: int
    last_wear_date: str | None
    created_at: str

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    """异步任务响应"""
    task_id: str
    status: str  # pending / processing / success / failed


class TaskStatusResponse(BaseModel):
    """任务状态查询响应"""
    task_id: str
    status: str
    garment_id: str | None = None
    error: str | None = None


class GarmentListResponse(BaseModel):
    """衣物列表响应（分页）"""
    items: list[GarmentResponse]
    total: int
    page: int
    page_size: int
