"""
services/task_manager.py — 异步任务管理器

功能：
1. 管理衣物上传后的异步处理任务（抠图 + 打标）
2. 提供任务状态查询
3. 使用 asyncio 后台执行，不阻塞请求

任务流程：
上传图片 → 创建任务(返回task_id) → 后台执行: 抠图→打标→保存→更新状态
前端轮询: GET /garments/status/{task_id}
"""

import asyncio
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import async_session
from ..models.garment import Garment
from ..schemas.garment import GarmentTags
from .bg_remove import remove_background, resize_image
from .llm_tag import tag_garment

logger = logging.getLogger(__name__)

# 任务状态存储（内存，MVP 够用）
_tasks: dict[str, dict] = {}


def get_task_status(task_id: str) -> dict | None:
    """查询任务状态"""
    return _tasks.get(task_id)


async def create_garment_task(
    user_id: str,
    file_bytes: bytes,
    filename: str,
) -> str:
    """
    创建衣物处理任务

    Args:
        user_id: 用户 ID
        file_bytes: 图片二进制
        filename: 原始文件名

    Returns:
        任务 ID
    """
    task_id = str(uuid.uuid4())
    _tasks[task_id] = {"status": "pending", "created_at": datetime.now(timezone.utc).isoformat()}

    # 后台异步执行
    asyncio.create_task(_process_garment(task_id, user_id, file_bytes, filename))

    return task_id


async def _process_garment(
    task_id: str,
    user_id: str,
    file_bytes: bytes,
    filename: str,
):
    """后台处理：抠图 → 打标 → 保存"""
    try:
        _tasks[task_id]["status"] = "processing"

        # 1. 缩放（用线程池避免阻塞事件循环）
        loop = asyncio.get_event_loop()
        file_bytes = await loop.run_in_executor(None, resize_image, file_bytes, 1024)

        # 2. 保存原图
        ext = Path(filename).suffix or ".jpg"
        original_name = f"{uuid.uuid4()}{ext}"
        original_path = Path(settings.UPLOAD_DIR) / original_name
        original_path.write_bytes(file_bytes)
        original_url = f"/static/uploads/{original_name}"
        logger.info(f"[{task_id[:8]}] 原图已保存: {original_name}")

        # 3. 抠图（用线程池避免阻塞事件循环）
        _tasks[task_id]["status"] = "removing_bg"
        loop = asyncio.get_event_loop()
        processed_bytes = await loop.run_in_executor(None, remove_background, file_bytes)

        processed_name = f"{uuid.uuid4()}.png"
        processed_path = Path(settings.UPLOAD_DIR) / processed_name
        processed_path.write_bytes(processed_bytes)
        processed_url = f"/static/uploads/{processed_name}"
        logger.info(f"[{task_id[:8]}] 抠图完成: {processed_name}")

        # 4. LLM 打标
        _tasks[task_id]["status"] = "tagging"
        tags = await tag_garment(processed_bytes)
        logger.info(f"[{task_id[:8]}] 打标完成: {tags.color} {tags.material}")

        # 5. 保存到数据库
        _tasks[task_id]["status"] = "saving"
        async with async_session() as db:
            garment = Garment(
                user_id=user_id,
                original_url=original_url,
                processed_url=processed_url,
                category=_guess_category(tags),
                tags=tags.model_dump_json(),
                temp_min=-30,  # 默认值，用户可修改
                temp_max=50,
            )
            db.add(garment)
            await db.commit()

            _tasks[task_id]["status"] = "success"
            _tasks[task_id]["garment_id"] = garment.id
            logger.info(f"[{task_id[:8]}] 衣物保存成功: {garment.id}")

    except Exception as e:
        logger.error(f"[{task_id[:8]}] 处理失败: {e}")
        _tasks[task_id]["status"] = "failed"
        _tasks[task_id]["error"] = str(e)


def _guess_category(tags: GarmentTags) -> str:
    """根据标签猜测衣物类别（简单规则）"""
    # 基于风格和材质的简单启发式
    text = f"{tags.material} {' '.join(tags.style)}".lower()

    if any(k in text for k in ["鞋", "靴", "sneaker", "shoe"]):
        return "鞋"
    if any(k in text for k in ["帽", "包", "围巾", "手套", "项链", "戒指", "耳环"]):
        return "配饰"
    if any(k in text for k in ["外套", "夹克", "大衣", "风衣", "羽绒服"]):
        return "外套"
    if any(k in text for k in ["裤", "裙", "短裤", "半裙"]):
        return "下装"
    return "上衣"  # 默认
