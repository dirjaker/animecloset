"""
services/bg_remove.py — 背景移除服务（rembg 本地推理）

功能：
1. 接受原始图片 bytes，返回透明背景 PNG bytes
2. 使用 rembg 的 u2net 模型本地推理
3. 首次运行自动下载模型（约170MB），后续使用缓存

性能：
- CPU 推理：单张约 3-8 秒（取决于图片大小和CPU性能）
- 模型缓存：~/.u2net/u2net.onnx
"""

import io
import logging
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


def remove_background(image_bytes: bytes) -> bytes:
    """
    移除图片背景

    Args:
        image_bytes: 原始图片的二进制数据

    Returns:
        透明背景 PNG 图片的二进制数据

    Raises:
        RuntimeError: 抠图失败
    """
    try:
        # 延迟导入 rembg（首次导入会加载模型，较慢）
        from rembg import remove

        logger.info("开始抠图处理...")
        # rembg 处理
        output_bytes = remove(image_bytes)
        logger.info("抠图完成")
        return output_bytes

    except ImportError:
        raise RuntimeError("rembg 未安装，请运行: pip install rembg[cpu]")
    except Exception as e:
        logger.error(f"抠图失败: {e}")
        raise RuntimeError(f"抠图处理失败: {e}")


def resize_image(image_bytes: bytes, max_size: int = 1024) -> bytes:
    """
    等比缩放图片（减少处理时间）

    Args:
        image_bytes: 原始图片
        max_size: 最大边长（像素）

    Returns:
        缩放后的图片 bytes（JPEG 格式）
    """
    img = Image.open(io.BytesIO(image_bytes))

    # 等比缩放
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
