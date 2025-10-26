import os
from src.config import ConfigManager

DEFAULT_SAVE_PATH = "./data/screenshots/"
DEFAULT_WEBP_QUALITY = 60
DEFAULT_IMG_MAX_WIDTH = 1280
DEFAULT_TIMEOUT = 30


def test_given_missing_config_when_configmanager_created_then_should_create_from_sample(
    tmp_path
):
    """
    config.ini가 없을 때 sample 파일을 복사하여 생성하는지 확인
    """
    config_file = tmp_path / "config.ini"
    sample_file = tmp_path / "config.sample.ini"
    sample_text = (
        "[SCREENSHOT]\n"
        "SAVE_PATH=./data/screenshots/\n"
        "WEBP_QUALITY=80\n"
        "IMG_MAX_WIDTH=1024\n"
        "TIMEOUT=10\n"
    )
    sample_file.write_text(sample_text)
    # 실제 파일 경로를 임시로 변경하여 테스트
    import src.config
    src.config.ConfigManager.CONFIG_FILE = str(config_file)
    src.config.ConfigManager.SAMPLE_FILE = str(sample_file)
    src.config.ConfigManager._instance = None  # 싱글턴 초기화
    manager = src.config.ConfigManager()
    assert os.path.exists(config_file)
    assert manager.SAVE_PATH == "./data/screenshots/"
    assert manager.WEBP_QUALITY == 80
    assert manager.IMG_MAX_WIDTH == 1024
    assert manager.TIMEOUT == 10


def test_given_configmanager_when_reload_invoked_then_should_reload():
    manager = ConfigManager()
    manager.reload()
    assert hasattr(manager, "_config")


def test_given_invalid_config_when_property_accessed_then_should_fallback(
    tmp_path
):
    import src.config
    src.config.ConfigManager._instance = None  # 싱글턴 초기화
    """
    configparser 객체에 값이 없을 때 fallback 값 반환 확인
    """
    config_file = tmp_path / "config.ini"
    config_file.write_text("")
    src.config.ConfigManager.CONFIG_FILE = str(config_file)
    manager = src.config.ConfigManager()
    assert manager.SAVE_PATH == DEFAULT_SAVE_PATH
    assert manager.WEBP_QUALITY == DEFAULT_WEBP_QUALITY
    assert manager.IMG_MAX_WIDTH == DEFAULT_IMG_MAX_WIDTH
    assert manager.TIMEOUT == DEFAULT_TIMEOUT


def test_given_valid_config_when_properties_accessed_then_should_return_expected(
):
    manager = ConfigManager()
    assert isinstance(manager.SAVE_PATH, str)
    assert isinstance(manager.WEBP_QUALITY, int)
    assert isinstance(manager.IMG_MAX_WIDTH, int)
    assert isinstance(manager.TIMEOUT, int)
