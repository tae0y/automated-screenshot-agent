import logging
import os
from logging import handlers
from uvicorn.logging import DefaultFormatter

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 로그 포맷터
formatter = logging.Formatter(
    "%(asctime)s\t[%(levelname)s]\t\t%(message)s"
)

# 로그파일 핸들러
file_handler = handlers.TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    encoding="utf-8",
    backupCount=60
)
file_handler.setFormatter(formatter)

# 로그스트림 핸들러
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, stream_handler]
)

# Uvicorn 로거 오버라이드
for uv_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    uv_logger = logging.getLogger(uv_logger_name)
    uv_logger.handlers = [file_handler, stream_handler]
    uv_logger.propagate = False


def get_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    return _logger
