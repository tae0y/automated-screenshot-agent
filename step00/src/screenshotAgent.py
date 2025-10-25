from src.config import ConfigManager
from src.logger import get_logger

_config = ConfigManager()
_config.reload()

logger = get_logger(__name__)
logger.info("ScreenshotAgent started!!")
