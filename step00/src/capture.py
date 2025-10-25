from src.logger import get_logger

_logger = get_logger(__name__)


def capture_one(url: str):
    """
    스크린샷 캡처 단건
    """
    _logger.debug(f"capture called for url: {url}")
    is_success = None
    # do something...
    # TODO: url 형식이 아닌경우 실패
    return is_success


def capture_all(urls: list[str]):
    """
    스크린샷 캡처 여러건
    """
    _logger.debug(f"capture called for urls: {urls}")
    passed_url = []
    failed_url = []
