# 导入所有模型，确保 SQLAlchemy 能解析关系引用
from .user import User
from .garment import Garment
from .outfit import Outfit
from .recommend_log import RecommendLog

__all__ = ["User", "Garment", "Outfit", "RecommendLog"]
