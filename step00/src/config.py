import configparser
import logging
import os

from src.models import UrlInfo
from src.logger import get_logger

logger = get_logger(__name__, level=logging.DEBUG)


class ConfigManager:
    _instance = None
    CONFIG_FILE = "config.ini"
    SAMPLE_FILE = "config.sample.ini"

    @property
    def URLS(self):
        urls: list[UrlInfo] = []
        if "URLS" in self._config:
            for name, url in self._config.items("URLS"):
                urls.append(UrlInfo(name=name, url=url))
        return urls

    @property
    def WEBP_QUALITY(self):
        return self._config.getint("SCREENSHOT", "WEBP_QUALITY", fallback=60)

    @property
    def IMG_MAX_WIDTH(self):
        return self._config.getint(
            "SCREENSHOT", "IMG_MAX_WIDTH", fallback=1280
        )

    @property
    def TIMEOUT(self):
        return self._config.getint("SCREENSHOT", "TIMEOUT", fallback=30)

    @property
    def SAVE_PATH(self):
        return self._config.get(
            "SCREENSHOT", "SAVE_PATH", fallback="./data/screenshots/"
        )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.load()
            self._initialized = True

    def load(self):
        """
        Load configuration from file
        """
        # Read the configuration file
        config_file_path = self.CONFIG_FILE
        sample_file_path = self.SAMPLE_FILE
        _config = configparser.ConfigParser()
        if not os.path.exists(config_file_path):
            logger.warning(f"Configuration from {config_file_path} not found.")
            with open(sample_file_path, 'r', encoding='utf-8') as sample_file:
                with open(config_file_path, 'w', encoding='utf-8') as config_file:
                    config_file.write(sample_file.read())
                    msg = (
                        f"Configuration from {sample_file_path} copied to "
                        f"{config_file_path}."
                    )
                    logger.info(msg)
        # Parse the configuration file
        try:
            _config.read(config_file_path, encoding="utf-8")
            self._config = _config
            msg = f"Configuration from {config_file_path} loaded successfully."
            logger.info(msg)
        except Exception as e:
            msg = f"Error loading configuration from {config_file_path}: {e}"
            logger.error(msg)
            raise

    def reload(self):
        """
        Reload configuration from file
        """
        self.load()
        logger.info("Configuration reloaded successfully.")
