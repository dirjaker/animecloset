"""
schemas/recommend.py — 推荐相关请求/响应模型
"""

from pydantic import BaseModel


class RecommendRequest(BaseModel):
    """穿搭推荐请求"""
    date: str                     # YYYY-MM-DD
    occasion: str = ""            # 场合（可选）
    extra_requirements: str = ""  # 额外需求（可选）


class RecommendResponse(BaseModel):
    """穿搭推荐响应"""
    date: str
    weather: str
    temperature: int
    selected_garments: list[dict]  # 选中的衣物详情
    reason: str                    # 推荐理由
    is_fallback: bool = False      # 是否为降级推荐
