import configparser
import logging
import os

from src.logger import get_logger

logger = get_logger(__name__, level=logging.DEBUG)


class ConfigManager:
    _instance = None

    @property
    def URLS(self):
        urls = []
        if "URLS" in self._config:
            for name, url in self._config.items("URLS"):
                urls.append({"name": name, "url": url})
        return urls

    @property
    def WEBP_QUALITY(self):
        return self._config.getint("SCREENSHOT", "WEBP_QUALITY", fallback=60)

    @property
    def IMG_MAX_WIDTH(self):
        return self._config.getint("SCREENSHOT", "IMG_MAX_WIDTH", fallback=1280)

    @property
    def TIMEOUT(self):
        return self._config.getint("SCREENSHOT", "TIMEOUT", fallback=30)

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
        CONFIG_FILE = "config.ini"
        SAMPLE_FILE = "config.sample.ini"
        _config = configparser.ConfigParser()
        if not os.path.exists(CONFIG_FILE):
            logger.warning(f"Configuration from {CONFIG_FILE} not found.")
            with open(SAMPLE_FILE, 'r') as sample_file:
                with open(CONFIG_FILE, 'w') as config_file:
                    config_file.write(sample_file.read())
                    logger.info(f"Configuration from {SAMPLE_FILE} copied to {CONFIG_FILE}.")
        # Parse the configuration file
        try:
            _config.read(CONFIG_FILE)
            self._config = _config
            logger.info(f"Configuration from {CONFIG_FILE} loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading configuration from {CONFIG_FILE}: {e}")
            raise

    def reload(self):
        """
        Reload configuration from file
        """
        self.load()
        logger.info("Configuration reloaded successfully.")
