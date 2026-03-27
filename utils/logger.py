"""Reusable logging helpers used across the project.

Provides a simple `get_logger` factory that configures a console
handler and optional rotating file handler. Designed to be lightweight
and safe to call multiple times.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

DEFAULT_LOG_LEVEL = logging.INFO


def configure_logger(
    name: Optional[str] = None,
    level: int = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """Configure and return a logger.

    This function is idempotent: calling it multiple times for the same
    logger name will not add duplicate handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(fmt)
        logger.addHandler(stream)

        if log_file:
            fh = RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
            fh.setFormatter(fmt)
            logger.addHandler(fh)

    return logger


def get_logger(
    name: Optional[str] = None,
    log_file: Optional[str] = None,
    level: int = DEFAULT_LOG_LEVEL,
) -> logging.Logger:
    """Convenience wrapper to get a configured logger.

    Example:
            logger = get_logger(__name__, log_file="/var/log/myapp.log")
    """
    return configure_logger(name, level=level, log_file=log_file)


__all__ = ["get_logger", "configure_logger"]
