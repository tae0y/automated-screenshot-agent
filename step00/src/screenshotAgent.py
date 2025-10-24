from src.config import ConfigManager
from src.logger import logger

_config = ConfigManager()
_config.reload()

logger.info("ScreenshotAgent started!!")
