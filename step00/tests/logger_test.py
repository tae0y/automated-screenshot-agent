import pytest
import logging
import os
from src.logger import get_logger, LOG_DIR, LOG_FILE


VALID_LOGGER_NAME = "testLogger"
INVALID_LOGGER_NAME = ""
LOG_ENTRY = "Integration test log entry"


@pytest.mark.parametrize("name", [INVALID_LOGGER_NAME])
def test_given_invalid_name_when_get_logger_invoked_then_should_return_logger(name):
    logger = get_logger(name)
    assert isinstance(logger, logging.Logger)
    assert logger.name == "root"  # Python 표준 동작


@pytest.mark.parametrize("name", [VALID_LOGGER_NAME])
def test_given_valid_name_when_get_logger_invoked_then_should_return_logger(name):
    logger = get_logger(name)
    assert isinstance(logger, logging.Logger)
    assert logger.name == name


@pytest.mark.parametrize("name,level", [("testLogger2", logging.ERROR), ("testLogger3", logging.INFO)])
def test_given_level_when_get_logger_invoked_then_should_set_level(name, level):
    logger = get_logger(name, level=level)
    assert logger.level == level


import tempfile

def test_given_logger_when_log_written_then_should_create_log_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "integration.log")
        # get_logger가 로그 파일 경로를 지정할 수 있도록 수정 필요 (아래는 예시)
        logger = get_logger("integrationLogger")
        handler = logging.FileHandler(log_file, encoding="utf-8")
        logger.addHandler(handler)
        logger.info(LOG_ENTRY)
        handler.flush()
        assert os.path.exists(log_file)
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert LOG_ENTRY in content
