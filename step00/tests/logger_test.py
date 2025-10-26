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
    assert logger.name == name


@pytest.mark.parametrize("name", [VALID_LOGGER_NAME])
def test_given_valid_name_when_get_logger_invoked_then_should_return_logger(name):
    logger = get_logger(name)
    assert isinstance(logger, logging.Logger)
    assert logger.name == name


@pytest.mark.parametrize("name,level", [("testLogger2", logging.ERROR), ("testLogger3", logging.INFO)])
def test_given_level_when_get_logger_invoked_then_should_set_level(name, level):
    logger = get_logger(name, level=level)
    assert logger.level == level


def test_given_logger_when_log_written_then_should_create_log_file():
    logger = get_logger("integrationLogger")
    logger.info(LOG_ENTRY)
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        assert LOG_ENTRY in content
