"""
categories.py — 统一衣物分类标准

所有涉及分类的地方都必须使用此模块的常量和函数。
包括：前端展示名、后端存储值、LLM 输出映射。

标准分类（5个）：
  上衣  — T恤、衬衫、毛衣等上半身穿搭
  下装  — 裤子、裙子、短裤等下半身穿搭
  外套  — 夹克、大衣、风衣等外层穿搭
  鞋    — 运动鞋、皮鞋、靴子等
  配饰  — 手表、包包、帽子、围巾等
"""

from enum import Enum


class Category(str, Enum):
    """标准衣物分类枚举"""
    TOP = "上衣"
    BOTTOM = "下装"
    OUTER = "外套"
    SHOES = "鞋"
    ACCESSORY = "配饰"


# 标准分类列表（用于推荐系统）
REQUIRED_CATEGORIES = [Category.TOP.value, Category.BOTTOM.value]
OPTIONAL_CATEGORIES = [Category.OUTER.value, Category.SHOES.value, Category.ACCESSORY.value]
ALL_CATEGORIES = REQUIRED_CATEGORIES + OPTIONAL_CATEGORIES

# 前端筛选标签配置（label: 展示名, value: 存储值）
FILTER_TABS = [
    {"label": "全部", "value": ""},
    {"label": "上衣", "value": "上衣"},
    {"label": "下装", "value": "下装"},
    {"label": "外套", "value": "外套"},
    {"label": "鞋", "value": "鞋"},
    {"label": "配饰", "value": "配饰"},
]

# 搭配槽位配置（按展示顺序）
OUTFIT_SLOTS = [
    {"category": "上衣", "label": "上衣", "required": True},
    {"category": "下装", "label": "下装", "required": True},
    {"category": "外套", "label": "外套", "required": False},
    {"category": "鞋", "label": "鞋", "required": False},
    {"category": "配饰", "label": "配饰", "required": False},
]

# LLM 输出 → 标准分类的映射表
# 解决 LLM 返回 "裤子"、"裙子"、"鞋子" 等非标准名称的问题
CATEGORY_ALIASES = {
    # 上衣
    "上衣": "上衣",
    "T恤": "上衣",
    "t恤": "上衣",
    "衬衫": "上衣",
    "毛衣": "上衣",
    "卫衣": "上衣",
    "背心": "上衣",
    "打底衫": "上衣",
    "polo": "上衣",
    "POLO": "上衣",
    # 下装
    "下装": "下装",
    "裤子": "下装",
    "裤": "下装",
    "牛仔裤": "下装",
    "休闲裤": "下装",
    "西裤": "下装",
    "短裤": "下装",
    "裙子": "下装",
    "裙": "下装",
    "短裙": "下装",
    "长裙": "下装",
    "半身裙": "下装",
    "连衣裙": "下装",  # 连衣裙特殊：同时归类为下装
    # 外套
    "外套": "外套",
    "夹克": "外套",
    " jacket": "外套",
    "大衣": "外套",
    "风衣": "外套",
    "羽绒服": "外套",
    "棉服": "外套",
    "西装外套": "外套",
    "开衫": "外套",
    "马甲": "外套",
    # 鞋
    "鞋": "鞋",
    "鞋子": "鞋",
    "运动鞋": "鞋",
    "皮鞋": "鞋",
    "靴子": "鞋",
    "凉鞋": "鞋",
    "拖鞋": "鞋",
    "板鞋": "鞋",
    "高跟鞋": "鞋",
    "帆布鞋": "鞋",
    # 配饰
    "配饰": "配饰",
    "手表": "配饰",
    "包包": "配饰",
    "包": "配饰",
    "帽子": "配饰",
    "围巾": "配饰",
    "项链": "配饰",
    "手链": "配饰",
    "戒指": "配饰",
    "耳环": "配饰",
    "墨镜": "配饰",
    "眼镜": "配饰",
    "腰带": "配饰",
    "领带": "配饰",
}


def normalize_category(raw: str) -> str:
    """
    将 LLM 返回的分类名映射为标准分类名。

    Args:
        raw: LLM 返回的原始分类名（如 "裤子"、"鞋子"）

    Returns:
        标准分类名（"上衣"/"下装"/"外套"/"鞋"/"配饰"）
        如果无法映射，默认返回 "上衣"
    """
    if not raw:
        return Category.TOP.value

    # 精确匹配
    if raw in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[raw]

    # 模糊匹配（包含关键词）
    raw_lower = raw.lower()
    for alias, standard in CATEGORY_ALIASES.items():
        if alias in raw_lower or raw_lower in alias:
            return standard

    # 无法映射时默认上衣（避免数据污染）
    return Category.TOP.value


def validate_category(category: str) -> bool:
    """验证是否为标准分类"""
    return category in ALL_CATEGORIES
