from urllib.parse import urlparse
from src.logger import get_logger

_logger = get_logger(__name__)


def capture_one(url: str):
    """
    스크린샷 캡처 단건
    """
    _logger.debug(f"capture called for url: {url}")
    
    # Validate URL format
    parsed = urlparse(url)
    # URL must have a scheme (http/https) and a network location (domain)
    if not all([parsed.scheme, parsed.netloc]):
        _logger.error(f"Invalid URL format: {url}")
        return False
    if parsed.scheme not in ['http', 'https']:
        _logger.error(f"Invalid URL scheme (must be http or https): {url}")
        return False
    
    is_success = None
    # do something...
    return is_success


def capture_all(urls: list[str]):
    """
    스크린샷 캡처 여러건
    """
    _logger.debug(f"capture called for urls: {urls}")
    passed_url = []
    failed_url = []
