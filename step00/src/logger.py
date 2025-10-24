import logging
import os

from logging import handlers


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s",
    handlers=[
        handlers.TimedRotatingFileHandler(
            LOG_FILE,
            when="midnight",
            interval=1,
            encoding="utf-8",
            backupCount=60
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_logger():
    return logger
