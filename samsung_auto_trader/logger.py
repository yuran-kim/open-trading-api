import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

class KSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(
            record.created,
            tz=ZoneInfo("Asia/Seoul")
        )

        if datefmt:
            return dt.strftime(datefmt + " %Z")

        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name or "samsung_auto_trader")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = KSTFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
