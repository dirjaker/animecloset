"""
api/ai.py — AI 智能穿搭功能

提供：
1. 智能穿搭推荐 - 结合天气+场合+已有衣物
2. 风格分析 - 分析穿衣偏好给出风格标签
3. 衣物识别 - 上传照片自动识别类型/颜色/材质
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.garment import Garment
from ..models.outfit import Outfit

router = APIRouter(prefix="/ai", tags=["AI"])


# ── 风格标签定义 ──
STYLE_TAGS = {
    "极简": {"keywords": ["白色", "黑色", "灰色", "基础款"], "desc": "简约至上，less is more"},
    "复古": {"keywords": ["格纹", "灯芯绒", "喇叭", "高腰"], "desc": "怀旧风格，经典不过时"},
    "街头": {"keywords": ["卫衣", "牛仔", "运动鞋", "宽松"], "desc": "随性自在，潮流前线"},
    "优雅": {"keywords": ["连衣裙", "高跟", "丝绸", "修身"], "desc": "精致得体，气质出众"},
    "运动": {"keywords": ["运动", "速干", "弹力", "跑步"], "desc": "活力四射，动感十足"},
    "休闲": {"keywords": ["T恤", "牛仔裤", "帆布鞋", "棉质"], "desc": "舒适自然，日常百搭"},
    "商务": {"keywords": ["西装", "衬衫", "皮鞋", "正式"], "desc": "专业干练，职场必备"},
    "文艺": {"keywords": ["棉麻", "碎花", "复古", "手工"], "desc": "清新脱俗，独特品味"},
}

# ── 天气穿衣建议 ──
WEATHER_OUTFIT_MAP = {
    "hot": {  # >= 30°C
        "temp_range": "30°C+",
        "suggestion": "炎热天气",
        "categories": ["短袖T恤", "短裤", "裙子", "凉鞋", "遮阳帽"],
        "materials": ["棉", "麻", "真丝"],
        "colors": ["白色", "浅色", "淡蓝", "米色"],
    },
    "warm": {  # 25-30°C
        "temp_range": "25-30°C",
        "suggestion": "温暖天气",
        "categories": ["短袖", "薄长裤", "连衣裙", "帆布鞋"],
        "materials": ["棉", "亚麻", "薄款面料"],
        "colors": ["浅色", "亮色", "粉色", "浅蓝"],
    },
    "mild": {  # 20-25°C
        "temp_range": "20-25°C",
        "suggestion": "舒适温度",
        "categories": ["长袖", "薄外套", "牛仔裤", "休闲鞋"],
        "materials": ["棉", "针织", "薄羊毛"],
        "colors": ["中性色", "暖色", "卡其色", "浅灰"],
    },
    "cool": {  # 15-20°C
        "temp_range": "15-20°C",
        "suggestion": "微凉天气",
        "categories": ["外套", "卫衣", "长裤", "运动鞋"],
        "materials": ["棉", "针织", "牛仔"],
        "colors": ["暖色", "深色", "棕色", "酒红"],
    },
    "cold": {  # 10-15°C
        "temp_range": "10-15°C",
        "suggestion": "较冷天气",
        "categories": ["厚外套", "毛衣", "长裤", "靴子"],
        "materials": ["羊毛", "羊绒", "厚棉"],
        "colors": ["深色", "暖色", "驼色", "深蓝"],
    },
    "very_cold": {  # < 10°C
        "temp_range": "<10°C",
        "suggestion": "寒冷天气",
        "categories": ["羽绒服", "厚毛衣", "围巾", "手套", "帽子"],
        "materials": ["羽绒", "羊毛", "羊绒"],
        "colors": ["深色", "暖色", "黑色", "深灰"],
    },
}


def get_temp_category(temp_c: str) -> str:
    """根据温度返回穿衣类别"""
    try:
        t = int(temp_c)
        if t >= 30: return "hot"
        if t >= 25: return "warm"
        if t >= 20: return "mild"
        if t >= 15: return "cool"
        if t >= 10: return "cold"
        return "very_cold"
    except (ValueError, TypeError):
        return "mild"


def analyze_garment_style(garment: dict) -> list[str]:
    """分析单件衣物的风格标签"""
    tags = []
    name = (garment.get("name", "") + " " + garment.get("category", "")).lower()
    color = garment.get("color", "").lower()
    material = garment.get("material", "").lower()
    
    for style, info in STYLE_TAGS.items():
        for keyword in info["keywords"]:
            if keyword in name or keyword in color or keyword in material:
                if style not in tags:
                    tags.append(style)
    
    return tags if tags else ["休闲"]


@router.get("/recommend")
async def get_ai_recommendation(
    city: str = Query("Beijing", description="城市名称"),
    occasion: str = Query("日常", description="场合：日常/工作/约会/运动"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI 智能穿搭推荐
    
    结合天气、场合、用户已有衣物进行推荐
    """
    # 1. 获取用户衣物
    result = await db.execute(
        select(Garment).where(Garment.user_id == user.id)
    )
    garments = result.scalars().all()
    
    if not garments:
        return {
            "recommendations": [],
            "message": "衣橱是空的，快去添加衣物吧！",
            "weather": None,
        }
    
    # 2. 获取天气数据
    weather_data = None
    temp_category = "mild"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://wttr.in/{city}?format=j1",
                headers={"Accept-Language": "zh-CN"},
            )
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_condition", [{}])[0]
                temp_c = current.get("temp_C", "20")
                temp_category = get_temp_category(temp_c)
                weather_data = {
                    "temp_c": temp_c,
                    "weather_desc": current.get("lang_zh", [{}])[0].get("value", ""),
                    "humidity": current.get("humidity", ""),
                }
    except Exception:
        pass
    
    # 3. 根据天气和场合推荐
    weather_info = WEATHER_OUTFIT_MAP.get(temp_category, WEATHER_OUTFIT_MAP["mild"])
    
    # 对衣物评分
    scored_garments = []
    for g in garments:
        score = 0
        g_dict = {
            "id": g.id,
            "name": g.name or g.category,
            "category": g.category,
            "color": g.color or "",
            "material": g.material or "",
            "image_url": g.image_url or g.thumbnail_url or g.processed_url or "",
            "season": g.season or "",
        }
        
        # 天气匹配加分
        for cat in weather_info["categories"]:
            if cat in g.category:
                score += 3
        
        # 材质匹配加分
        for mat in weather_info["materials"]:
            if mat in (g.material or ""):
                score += 2
        
        # 颜色匹配加分
        for color in weather_info["colors"]:
            if color in (g.color or ""):
                score += 1
        
        # 季节匹配加分
        if g.season:
            if temp_category in ["hot", "warm"] and "夏" in g.season:
                score += 2
            elif temp_category in ["cold", "very_cold"] and "冬" in g.season:
                score += 2
            elif temp_category in ["mild", "cool"] and ("春" in g.season or "秋" in g.season):
                score += 2
        
        # 穿着次数加分（常穿的优先）
        if g.wear_count:
            score += min(g.wear_count // 5, 3)
        
        scored_garments.append({**g_dict, "score": score, "style_tags": analyze_garment_style(g_dict)})
    
    # 按分数排序，取 top 5
    scored_garments.sort(key=lambda x: x["score"], reverse=True)
    top_garments = scored_garments[:5]
    
    # 4. 生成推荐理由
    recommendation_reason = f"根据{city}当前{weather_info['suggestion']}"
    if weather_data:
        recommendation_reason += f"（{weather_data['temp_c']}°C）"
    recommendation_reason += f"，为您推荐以下{occasion}穿搭："
    
    return {
        "recommendations": top_garments,
        "weather": weather_data,
        "temp_category": temp_category,
        "occasion": occasion,
        "reason": recommendation_reason,
        "outfit_tips": [
            f"建议穿着：{'、'.join(weather_info['categories'][:3])}",
            f"推荐材质：{'、'.join(weather_info['materials'])}",
            f"推荐色系：{'、'.join(weather_info['colors'])}",
        ],
    }


@router.get("/style-analysis")
async def get_style_analysis(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI 风格分析
    
    分析用户的穿衣偏好，给出风格标签和建议
    """
    # 1. 获取用户所有衣物
    result = await db.execute(
        select(Garment).where(Garment.user_id == user.id)
    )
    garments = result.scalars().all()
    
    if not garments:
        return {
            "style_profile": {},
            "main_style": "未知",
            "message": "衣橱是空的，无法分析风格",
        }
    
    # 2. 统计各类别数量
    category_count = {}
    color_count = {}
    material_count = {}
    season_count = {}
    style_scores = {style: 0 for style in STYLE_TAGS}
    
    for g in garments:
        # 类别统计
        cat = g.category or "其他"
        category_count[cat] = category_count.get(cat, 0) + 1
        
        # 颜色统计
        color = g.color or "未知"
        color_count[color] = color_count.get(color, 0) + 1
        
        # 材质统计
        if g.material:
            material_count[g.material] = material_count.get(g.material, 0) + 1
        
        # 季节统计
        if g.season:
            season_count[g.season] = season_count.get(g.season, 0) + 1
        
        # 风格评分
        g_dict = {
            "name": g.name or g.category,
            "category": g.category,
            "color": g.color or "",
            "material": g.material or "",
        }
        for tag in analyze_garment_style(g_dict):
            style_scores[tag] += 1
    
    # 3. 计算风格占比
    total_garments = len(garments)
    style_percentages = {}
    for style, score in style_scores.items():
        if score > 0:
            style_percentages[style] = round(score / total_garments * 100, 1)
    
    # 4. 排序得到主要风格
    sorted_styles = sorted(style_percentages.items(), key=lambda x: x[1], reverse=True)
    main_style = sorted_styles[0][0] if sorted_styles else "休闲"
    
    # 5. 生成风格报告
    top_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)[:5]
    top_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 6. 生成建议
    suggestions = []
    
    if len(category_count) < 3:
        suggestions.append("衣橱品类较少，建议丰富基础款")
    
    if len(color_count) < 3:
        suggestions.append("颜色较为单一，可以尝试更多色彩搭配")
    
    main_style_info = STYLE_TAGS.get(main_style, {})
    suggestions.append(f"您的主要风格是「{main_style}」，{main_style_info.get('desc', '')}")
    
    if "极简" in style_percentages and style_percentages["极简"] > 50:
        suggestions.append("极简风格为主，可以适当加入配饰增加亮点")
    
    return {
        "total_garments": total_garments,
        "main_style": main_style,
        "style_tags": sorted_styles,
        "top_categories": top_categories,
        "top_colors": top_colors,
        "materials": sorted(material_count.items(), key=lambda x: x[1], reverse=True)[:5],
        "seasons": season_count,
        "suggestions": suggestions,
        "style_description": main_style_info.get("desc", ""),
    }


@router.post("/identify-garment")
async def identify_garment(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """AI 衣物识别
    
    上传照片，自动识别衣物类型、颜色、材质等信息
    注意：当前版本使用规则匹配，后续可接入真正的 AI 视觉模型
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    
    # 验证文件大小 (10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 10MB")
    
    # 保存图片
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"identify_{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = Path(__file__).parent.parent.parent / "uploads" / "identify"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    image_url = f"/uploads/identify/{filename}"
    
    # 返回识别结果模板（用户可以手动修正）
    # 在实际应用中，这里会调用 AI 视觉模型进行识别
    return {
        "image_url": image_url,
        "identified": {
            "category": "待确认",
            "color": "待确认",
            "material": "待确认",
            "season": "四季",
            "confidence": 0,
        },
        "suggested_categories": [
            "T恤", "衬衫", "外套", "裤子", "裙子", "鞋子", "配饰"
        ],
        "suggested_colors": [
            "黑色", "白色", "灰色", "蓝色", "红色", "绿色", "黄色", "粉色", "棕色", "米色"
        ],
        "suggested_materials": [
            "棉", "麻", "丝绸", "羊毛", "牛仔", "皮革", "聚酯纤维", "针织"
        ],
        "message": "请确认或修正识别结果",
    }
