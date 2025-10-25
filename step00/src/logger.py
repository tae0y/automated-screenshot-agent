import logging
import os

from logging import handlers


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.DEBUG,
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


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Get a logger instance
    - name: Logger name, pass __name__ typically
    - level: Logging level, default to INFO
    """
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    return _logger
