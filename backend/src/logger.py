import json
import logging
import sys
from datetime import UTC, datetime

from app.g import request_id_var, user_id_var


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
            **getattr(record, "fields", {}),
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def setup_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestContextFilter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
    for noisy_library in ("pymongo", "redis"):
        logging.getLogger(noisy_library).setLevel(logging.WARNING)


logger = logging.getLogger("skim")
