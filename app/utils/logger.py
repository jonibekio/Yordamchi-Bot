import logging
import re
import sys
from typing import Optional

# Windows terminalida UTF-8 va emojilar to'g'ri chiqishi uchun
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class SensitiveFilter(logging.Filter):
    """
    Loglarda API kalitlar va bot tokenlari chiqib ketishining oldini oluvchi filtr.
    """
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.patterns = [
            re.compile(r"bot\d+:[A-Za-z0-9_-]{35}", re.IGNORECASE),
            re.compile(r"sk-[A-Za-z0-9_-]{20,}", re.IGNORECASE),
            re.compile(r"password=([^\s&]+)", re.IGNORECASE),
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in self.patterns:
                record.msg = pattern.sub("[MAXFIY MA'LUMOT]", record.msg)
        return True


def setup_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name or "bot_app")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveFilter())
        logger.addHandler(handler)

    return logger
