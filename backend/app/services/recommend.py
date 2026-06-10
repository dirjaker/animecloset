"""
services/recommend.py — 穿搭推荐算法

核心流程：
1. 获取天气（温度+天气状况）
2. 按温度筛选衣物
3. 按场合筛选（可选，不足则放宽）
4. 冷宫唤醒（优先推荐30天未穿的衣物）
5. 调用 LLM 生成穿搭组合
6. 降级：LLM 不可用时随机选择

输入：日期、场合（可选）、额外需求（可选）
输出：推荐衣物列表 + 推荐理由 + 天气信息
"""

import json
import random
import logging
from datetime import date, timedelta
from collections import defaultdict

import httpx

from ..core.config import settings
from ..core.database import async_session
from ..core.categories import (
    REQUIRED_CATEGORIES, OPTIONAL_CATEGORIES, ALL_CATEGORIES,
    normalize_category, OUTFIT_SLOTS,
)
from ..models.garment import Garment
from ..schemas.garment import GarmentTags
from .weather import get_weather
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def recommend_outfit(
    user_id: str,
    target_date: str,
    occasion: str = "",
    extra_requirements: str = "",
    city: str = "北京",
) -> dict:
    """
    生成穿搭推荐

    Args:
        user_id: 用户 ID
        target_date: 目标日期 YYYY-MM-DD
        occasion: 场合
        extra_requirements: 额外需求
        city: 城市

    Returns:
        {
            "date": "2024-06-15",
            "weather": "晴",
            "temperature": 28,
            "selected_garments": [...],
            "reason": "推荐理由",
            "is_fallback": False
        }
    """
    # 1. 获取天气
    weather_info = await get_weather(city)
    temperature = weather_info["temperature"]
    weather_text = weather_info["weather"]

    # 2. 获取用户衣橱
    async with async_session() as db:
        result = await db.execute(
            select(Garment).where(Garment.user_id == user_id)
        )
        all_garments = result.scalars().all()

    if not all_garments:
        return {
            "date": target_date,
            "weather": weather_text,
            "temperature": temperature,
            "selected_garments": [],
            "reason": "衣橱是空的，快去添加衣物吧！",
            "is_fallback": True,
        }

    # 3. 按温度筛选
    temp_filtered = [
        g for g in all_garments
        if g.temp_min <= temperature <= g.temp_max
    ]
    if not temp_filtered:
        temp_filtered = all_garments  # 温度范围都不匹配，放宽

    # 4. 按场合筛选
    if occasion:
        occasion_filtered = _filter_by_occasion(temp_filtered, occasion)
        if len(occasion_filtered) < 3:
            occasion_filtered = temp_filtered  # 不足3件，放宽
    else:
        occasion_filtered = temp_filtered

    # 5. 冷宫唤醒：标记30天未穿的衣物
    cold_palace_ids = _get_cold_palace_ids(occasion_filtered)

    # 6. 按类别分组（使用标准分类）
    by_category = _group_by_category(occasion_filtered)

    # 7. 检查必要类别
    for cat in REQUIRED_CATEGORIES:
        if not by_category.get(cat):
            return {
                "date": target_date,
                "weather": weather_text,
                "temperature": temperature,
                "selected_garments": [],
                "reason": f"缺少{cat}，请先添加",
                "is_fallback": True,
            }

    # 8. 调用 LLM 推荐
    try:
        result = await _call_llm_recommend(
            by_category, weather_text, temperature,
            occasion, extra_requirements, cold_palace_ids, target_date
        )
        return {
            "date": target_date,
            "weather": weather_text,
            "temperature": temperature,
            **result,
            "is_fallback": False,
        }
    except Exception as e:
        logger.error(f"LLM 推荐失败: {e}，使用降级方案")
        return _fallback_recommend(
            by_category, weather_text, temperature, target_date
        )


def _filter_by_occasion(garments: list[Garment], occasion: str) -> list[Garment]:
    """按场合筛选衣物"""
    result = []
    for g in garments:
        tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
        if occasion in tags.occasion or "日常" in tags.occasion:
            result.append(g)
    return result


def _get_cold_palace_ids(garments: list[Garment]) -> set[str]:
    """找出30天未穿的衣物ID"""
    cutoff = date.today() - timedelta(days=30)
    return {
        g.id for g in garments
        if g.last_wear_date is None or g.last_wear_date < cutoff
    }


def _group_by_category(garments: list[Garment]) -> dict[str, list[Garment]]:
    """
    按标准类别分组

    使用 normalize_category 确保所有分类名都映射到标准值。
    """
    groups = defaultdict(list)
    for g in garments:
        # 标准化分类名（处理旧数据中的非标准分类）
        std_cat = normalize_category(g.category)
        groups[std_cat].append(g)
    return dict(groups)


async def _call_llm_recommend(
    by_category: dict,
    weather: str,
    temperature: int,
    occasion: str,
    extra: str,
    cold_palace_ids: set[str],
    target_date: str,
) -> dict:
    """调用 LLM 生成穿搭推荐"""
    # 构建候选衣物列表
    candidates = []
    for cat, garments in by_category.items():
        for g in garments[:5]:  # 每类最多5件
            tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
            is_cold = "❄️很久没穿了" if g.id in cold_palace_ids else ""
            candidates.append({
                "id": g.id,
                "category": cat,
                "color": tags.color,
                "style": tags.style,
                "is_cold": is_cold,
            })

    prompt = f"""你是一个专业的穿搭顾问。请根据以下信息推荐一套穿搭。

日期：{target_date}
天气：{weather}，温度：{temperature}℃
场合：{occasion or '日常'}
额外需求：{extra or '无'}

候选衣物：
{json.dumps(candidates, ensure_ascii=False, indent=2)}

请返回JSON格式：
{{
  "selected_ids": ["上衣ID", "下装ID", "外套ID(可选)", "鞋ID(可选)", "配饰ID(可选)"],
  "reason": "推荐理由（简短，50字以内）"
}}

注意：
- selected_ids 中必须从候选衣物中选择
- 标记了❄️很久没穿的衣物请优先考虑
- 推荐理由要包含天气和场合信息
- 只返回JSON，不要额外文字"""

    if not settings.DEEPSEEK_API_KEY:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY")

    url = f"{settings.DEEPSEEK_BASE_URL}/chat/completions"
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

    # 解析响应
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]

    data = json.loads(content.strip())
    selected_ids = data.get("selected_ids", [])
    reason = data.get("reason", "")

    # 验证 ID 有效性
    all_ids = {g.id for garments in by_category.values() for g in garments}
    valid_ids = [sid for sid in selected_ids if sid in all_ids]

    # 构建选中衣物详情
    all_garments = {g.id: g for garments in by_category.values() for g in garments}
    selected_garments = []
    for gid in valid_ids:
        g = all_garments[gid]
        tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
        selected_garments.append({
            "id": g.id,
            "category": normalize_category(g.category),  # 确保返回标准分类
            "tags": tags.model_dump(),
            "processed_url": g.processed_url,
            "is_cold_palace": gid in cold_palace_ids,
        })

    return {"selected_garments": selected_garments, "reason": reason}


def _fallback_recommend(
    by_category: dict, weather: str, temperature: int, target_date: str
) -> dict:
    """降级推荐：随机选择"""
    selected = []

    for cat in ALL_CATEGORIES:
        garments = by_category.get(cat, [])
        if garments:
            g = random.choice(garments)
            tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
            selected.append({
                "id": g.id,
                "category": normalize_category(g.category),
                "tags": tags.model_dump(),
                "processed_url": g.processed_url,
                "is_cold_palace": False,
            })

    return {
        "date": target_date,
        "weather": weather,
        "temperature": temperature,
        "selected_garments": selected,
        "reason": f"根据{weather}{temperature}℃为您选择的基础搭配，您可以手动调整。",
        "is_fallback": True,
    }
