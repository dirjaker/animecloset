"""
api/recommend.py — 推荐接口

POST /api/recommend — 获取穿搭推荐
"""

from fastapi import APIRouter, Depends

from ..core.security import get_current_user
from ..models.user import User
from ..schemas.recommend import RecommendRequest, RecommendResponse
from ..services.recommend import recommend_outfit

router = APIRouter(prefix="/recommend", tags=["推荐"])


@router.post("", response_model=RecommendResponse)
async def get_recommendation(
    req: RecommendRequest,
    user: User = Depends(get_current_user),
):
    """
    获取穿搭推荐

    输入：日期、场合（可选）、额外需求（可选）
    输出：推荐穿搭组合 + 推荐理由 + 天气信息
    """
    result = await recommend_outfit(
        user_id=user.id,
        target_date=req.date,
        occasion=req.occasion,
        extra_requirements=req.extra_requirements,
    )
    return RecommendResponse(**result)
