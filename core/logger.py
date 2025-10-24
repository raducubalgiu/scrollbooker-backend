import os
import sys
import structlog
from loguru import logger
from datetime import datetime
from pathlib import Path

log_dir = Path(__file__).resolve().parent.parent

if not log_dir.exists():
    os.makedirs(log_dir, exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="INFO",
    colorize=True,
    enqueue=True
)

logger.add(
    log_dir / f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log",
    level="INFO",
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
    enqueue=True
)

# Configure Structlog for structured logs
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

# Create global loggers
struct_logger = structlog.get_logger()

# Expose them for direct import
__all__ = ["logger", "struct_logger"]