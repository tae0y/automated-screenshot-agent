from src.logger import get_logger
from src.models import UrlInfo

_logger = get_logger(__name__)


def is_valid_url(url: str) -> bool:
    """
    URL 유효성 검사
    - param
        - url: 검사 대상 URL
    - return
        - is_valid: 유효성 검사 결과
    """
    # TODO: URL 유효성 검사 개선
    return url.startswith("http://") or url.startswith("https://")


def capture_one(url: UrlInfo) -> bool:
    """
    스크린샷 캡처 단건
    - param
        - url: 스크린샷 캡처 대상 URL
    - return
        - is_success: 캡처 성공 여부
    """
    _logger.debug(f"capture called for one url: {url}")
    is_success = None

    if not is_valid_url(url.url):
        _logger.error(f"Invalid URL format: {url.url}")
        raise ValueError(f"Invalid URL format: {url.url}")

    try:
        # TODO: 실제 캡처로직 수행
        is_success = True
    except Exception as e:
        _logger.error(f"Error occurred while capturing {url}: {e}")
        is_success = False

    return is_success


def capture_all(urls: list[UrlInfo]) -> tuple[list[UrlInfo], list[UrlInfo]]:
    """
    스크린샷 캡처 여러건
    - param
        - urls: 스크린샷 캡처 대상 URL 리스트
    - return
        - passed_url: 캡처 성공한 URL 리스트
        - failed_url: 캡처 실패한 URL 리스트
    """
    _logger.debug(f"capture called for multi urls: {urls}")

    passed_url = []
    failed_url = []

    if not urls or len(urls) < 2:
        raise ValueError("urls must contain at least two URLs.")

    for url in urls:
        is_success = capture_one(url)
        try:
            if is_success:
                passed_url.append(url)
            else:
                failed_url.append(url)
        except Exception as e:
            _logger.error(f"Error occurred while capturing {url}: {e}")
            failed_url.append(url)

    return passed_url, failed_url
