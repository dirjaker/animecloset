"""
services/llm_tag.py — 衣物打标服务（支持视觉模型）

功能：
1. 输入衣物图片，使用视觉模型识别衣物属性
2. 支持通义千问 (Qwen-VL) 进行图片分类
3. 如果视觉模型不可用，使用本地规则推断
4. 输出结构化标签（颜色、材质、风格、季节、场合、温度范围、分类）

模型分工：
- 图片分类：通义千问 VL (qwen-vl-max) 或其他视觉模型
- 文本任务：DeepSeek (推荐、搭配建议等)
"""

import json
import base64
import logging
import re

import httpx

from ..core.config import settings
from ..core.categories import normalize_category, ALL_CATEGORIES
from ..schemas.garment import GarmentTags

logger = logging.getLogger(__name__)

# 视觉模型打标提示词
TAG_PROMPT_VISION = """你是一个专业的服装鉴定师。请分析这张衣物图片，返回以下JSON格式的标签：

{
  "category": "衣物分类",
  "color": "主颜色",
  "material": "材质",
  "style": ["风格1", "风格2"],
  "season": ["适宜季节"],
  "occasion": ["适宜场合"],
  "temp_min": 适宜最低温度(整数,摄氏度),
  "temp_max": 适宜最高温度(整数,摄氏度)
}

字段说明：
- category 必须是以下之一：上衣、下装、外套、鞋、配饰
- color 常见值：黑色、白色、灰色、红色、蓝色、绿色、黄色、粉色、棕色、藏青色、卡其色
- material 常见值：棉、涤纶、丝绸、牛仔布、皮革、羊毛、亚麻、尼龙
- style 可选值：休闲、商务、运动、正式、街头、复古、简约、甜美
- season 可选值：春、夏、秋、冬
- occasion 可选值：工作、日常、聚会、户外、运动、正式场合
- 温度范围根据衣物厚度和材质合理推断

只返回JSON，不要任何额外文字。"""

# 文本打标提示词
TAG_PROMPT_TEXT = """你是一个专业的服装鉴定师。用户会描述一件衣物，请返回以下JSON格式的标签：

{
  "category": "衣物分类",
  "color": "主颜色",
  "material": "材质",
  "style": ["风格1", "风格2"],
  "season": ["适宜季节"],
  "occasion": ["适宜场合"],
  "temp_min": 适宜最低温度(整数,摄氏度),
  "temp_max": 适宜最高温度(整数,摄氏度)
}

字段说明：
- category 必须是以下之一：上衣、下装、外套、鞋、配饰
- color 常见值：黑色、白色、灰色、红色、蓝色、绿色、黄色、粉色、棕色、藏青色、卡其色
- material 常见值：棉、涤纶、丝绸、牛仔布、皮革、羊毛、亚麻、尼龙
- style 可选值：休闲、商务、运动、正式、街头、复古、简约、甜美
- season 可选值：春、夏、秋、冬
- occasion 可选值：工作、日常、聚会、户外、运动、正式场合
- 温度范围根据衣物厚度和材质合理推断

只返回JSON，不要任何额外文字。"""


async def tag_garment(image_bytes: bytes, hint_category: str = "") -> tuple[str, GarmentTags]:
    """
    为衣物图片打标

    Args:
        image_bytes: 衣物图片的二进制数据
        hint_category: 用户指定的分类（可选，用于辅助验证）

    Returns:
        (标准化分类, GarmentTags)
    """
    # 优先使用用户指定的分类
    if hint_category:
        category = normalize_category(hint_category)
        return category, _default_tags_for_category(category)

    # 尝试视觉模型打标
    if settings.DASHSCOPE_API_KEY:
        try:
            logger.info("尝试使用通义千问 VL 进行图片分类...")
            category, tags = await _tag_with_vision_model(image_bytes)
            return normalize_category(category), tags
        except Exception as e:
            logger.warning(f"视觉模型调用失败: {e}，回退到本地规则")

    # 使用本地规则推断（默认返回上衣）
    logger.info("使用本地规则推断分类")
    return "上衣", _default_tags()


async def _tag_with_vision_model(image_bytes: bytes) -> tuple[str, GarmentTags]:
    """
    使用通义千问 VL 进行图片分类

    API: DashScope (阿里云百炼)
    模型: qwen-vl-max 或 qwen-vl-plus
    """
    # 将图片转为 base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:image/jpeg;base64,{image_base64}"

    # DashScope API 端点
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    payload = {
        "model": "qwen3-vl-plus",  # 阿里云百炼视觉模型
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": TAG_PROMPT_VISION},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        logger.info(f"视觉模型返回: {content[:200]}...")

        # 解析 JSON 响应
        raw_category, tags = _parse_llm_response(content)
        return raw_category, tags


async def tag_garment_with_text(description: str) -> tuple[str, GarmentTags]:
    """
    使用文本描述为衣物打标（备用方案）

    Args:
        description: 衣物的文本描述（如 "白色棉质T恤"）

    Returns:
        (标准化分类, GarmentTags)
    """
    if not settings.DEEPSEEK_API_KEY:
        # 从描述中推断分类
        category = _infer_category_from_text(description)
        return category, _default_tags_for_category(category)

    try:
        # 调用 DeepSeek LLM
        response = await _call_llm_text(description)
        raw_category, tags = _parse_llm_response(response)
        category = normalize_category(raw_category)
        return category, tags

    except Exception as e:
        logger.error(f"LLM 打标失败: {e}")
        category = _infer_category_from_text(description)
        return category, _default_tags_for_category(category)


async def _call_llm_text(description: str) -> str:
    """调用 DeepSeek LLM 文本接口"""
    url = f"{settings.DEEPSEEK_BASE_URL}/chat/completions"

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": f"{TAG_PROMPT_TEXT}\n\n衣物描述：{description}"}
        ],
        "max_tokens": 500,
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _parse_llm_response(response: str) -> tuple[str, GarmentTags]:
    """解析 LLM 返回的 JSON"""
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    data = json.loads(text)
    raw_category = data.get("category", "上衣")

    tags = GarmentTags(
        color=data.get("color", ""),
        material=data.get("material", ""),
        style=data.get("style", []),
        season=data.get("season", []),
        occasion=data.get("occasion", []),
    )

    return raw_category, tags


def _default_tags() -> GarmentTags:
    """默认标签"""
    return GarmentTags(
        color="未知",
        material="未知",
        style=["休闲"],
        season=["春", "夏", "秋", "冬"],
        occasion=["日常"],
    )


def _default_tags_for_category(category: str) -> GarmentTags:
    """根据分类返回默认标签"""
    base_tags = _default_tags()

    # 根据分类调整默认值
    if category == "鞋":
        base_tags.material = "合成材料"
        base_tags.style = ["运动", "休闲"]
    elif category == "外套":
        base_tags.material = "棉"
        base_tags.style = ["休闲"]
        base_tags.season = ["春", "秋", "冬"]
    elif category == "配饰":
        base_tags.material = "金属"
        base_tags.style = ["简约"]

    return base_tags


def _infer_category_from_text(text: str) -> str:
    """从文本描述中推断分类"""
    text_lower = text.lower()

    # 鞋类关键词
    shoe_keywords = ["鞋", "靴", "sneaker", "shoe", "boot", "凉鞋", "拖鞋", "板鞋", "高跟鞋"]
    if any(kw in text_lower for kw in shoe_keywords):
        return "鞋"

    # 配饰关键词
    accessory_keywords = ["手表", "包", "帽子", "围巾", "项链", "戒指", "耳环", "墨镜", "眼镜", "腰带", "领带"]
    if any(kw in text_lower for kw in accessory_keywords):
        return "配饰"

    # 外套关键词
    outer_keywords = ["外套", "夹克", "大衣", "风衣", "羽绒服", "棉服", "西装外套", "开衫", "马甲"]
    if any(kw in text_lower for kw in outer_keywords):
        return "外套"

    # 下装关键词
    bottom_keywords = ["裤子", "裤", "牛仔裤", "休闲裤", "西裤", "短裤", "裙子", "裙", "短裙", "长裙"]
    if any(kw in text_lower for kw in bottom_keywords):
        return "下装"

    # 默认上衣
    return "上衣"
