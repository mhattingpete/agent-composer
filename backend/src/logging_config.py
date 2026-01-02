"""Logging configuration using loguru.

Provides unified logging for the application and third-party libraries.
Configures console output (INFO+) and rotating file logs (DEBUG+).
"""

import logging
import sys
from pathlib import Path

from loguru import logger

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class InterceptHandler(logging.Handler):
    """Route stdlib logging to loguru for unified log handling.

    Third-party libraries (Agno, FastAPI, uvicorn) use stdlib logging.
    This handler captures their logs and routes them through loguru
    for consistent formatting across all log sinks.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """Configure logging for the application.

    Sets up:
    - Console: INFO+ with colors
    - File: DEBUG+ with rotation (10MB, 7 days retention)
    - Intercepts stdlib logging for third-party libraries
    """
    # Remove default handler
    logger.remove()

    # Console: INFO and above with colors
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    )

    # File: DEBUG and above, with rotation
    logger.add(
        LOG_DIR / "agent.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
    )

    # Route all stdlib logging to loguru (for third-party libs)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set Agno loggers to DEBUG so their messages flow to loguru
    logging.getLogger("agno.agent.agent").setLevel(logging.DEBUG)
    logging.getLogger("agno.team.team").setLevel(logging.DEBUG)
