import os
from src.config import ConfigManager

DEFAULT_SAVE_PATH = "./data/screenshots/"
DEFAULT_WEBP_QUALITY = 60
DEFAULT_IMG_MAX_WIDTH = 1280
DEFAULT_TIMEOUT = 30


def test_given_missing_config_when_configmanager_created_then_should_create_from_sample(tmp_path, monkeypatch):
    # config.ini, config.sample.ini 경로를 임시 디렉터리로 변경
    config_file = tmp_path / "config.ini"
    sample_file = tmp_path / "config.sample.ini"
    sample_file.write_text("[SCREENSHOT]\nSAVE_PATH=./data/screenshots/\nWEBP_QUALITY=80\nIMG_MAX_WIDTH=1024\nTIMEOUT=10\n")
    monkeypatch.setattr("src.config.CONFIG_FILE", str(config_file))
    monkeypatch.setattr("src.config.SAMPLE_FILE", str(sample_file))
    # config.ini가 없을 때 생성되는지 확인
    manager = ConfigManager()
    assert os.path.exists(config_file)
    assert manager.SAVE_PATH == "./data/screenshots/"
    assert manager.WEBP_QUALITY == 80
    assert manager.IMG_MAX_WIDTH == 1024
    assert manager.TIMEOUT == 10


def test_given_configmanager_when_reload_invoked_then_should_reload(monkeypatch):
    manager = ConfigManager()
    monkeypatch.setattr(manager, "load", lambda: setattr(manager, "_config", manager._config))
    manager.reload()
    assert hasattr(manager, "_config")


def test_given_invalid_config_when_property_accessed_then_should_fallback(monkeypatch):
    manager = ConfigManager()
    # _config에 잘못된 값 주입
    manager._config = {}
    assert manager.SAVE_PATH == DEFAULT_SAVE_PATH
    assert manager.WEBP_QUALITY == DEFAULT_WEBP_QUALITY
    assert manager.IMG_MAX_WIDTH == DEFAULT_IMG_MAX_WIDTH
    assert manager.TIMEOUT == DEFAULT_TIMEOUT


def test_given_valid_config_when_properties_accessed_then_should_return_expected():
    manager = ConfigManager()
    assert isinstance(manager.SAVE_PATH, str)
    assert isinstance(manager.WEBP_QUALITY, int)
    assert isinstance(manager.IMG_MAX_WIDTH, int)
    assert isinstance(manager.TIMEOUT, int)
