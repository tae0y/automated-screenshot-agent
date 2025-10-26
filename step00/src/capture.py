import asyncio
import time

from urllib.parse import urlparse
from playwright.async_api import async_playwright
from src.config import ConfigManager
from src.logger import get_logger
from src.models import UrlInfo

_logger = get_logger(__name__)
_config = ConfigManager()


def is_valid_url(url: str) -> bool:
    """
    URL 유효성 검사
    - param
        - url: 검사 대상 URL
    - return
        - is_valid: 유효성 검사 결과
    """
    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        _logger.error(f"Invalid URL format: {url}")
        return False
    if parsed.scheme not in ['http', 'https']:
        _logger.error(f"Invalid URL scheme (must be http or https): {url}")
        return False
    return True


async def capture_one(urlinfo: UrlInfo) -> bool:
    """
    스크린샷 캡처 단건
    - param
        - url: 스크린샷 캡처 대상 URL
    - return
        - is_success: 캡처 성공 여부
    """
    _logger.debug(f"capture called for one url: {urlinfo}")
    is_success = None
    save_path = _config.SAVE_PATH

    if not is_valid_url(urlinfo.url):
        _logger.error(f"Invalid URL format: {urlinfo.url}")
        raise ValueError(f"Invalid URL format: {urlinfo.url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(urlinfo.url, wait_until="networkidle")
            except Exception as e:
                _logger.warning(f"Network idle not reached for {urlinfo.url}: {e}")
                await page.goto(urlinfo.url)  # 강제 캡처를 위해 재시도

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = f"{save_path}/{urlinfo.name}-{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            _logger.info(f"Screenshot saved: {screenshot_path}")
            await browser.close()
        is_success = True
    except Exception as e:
        _logger.error(f"Error occurred while capturing {urlinfo.url}: {e}")
        is_success = False

    return is_success


async def capture_all(urlinfos: list[UrlInfo]) -> tuple[list[UrlInfo], list[UrlInfo]]:
    """
    스크린샷 캡처 여러건
    - param
        - urls: 스크린샷 캡처 대상 URL 리스트
    - return
        - passed_url: 캡처 성공한 URL 리스트
        - failed_url: 캡처 실패한 URL 리스트
    """
    _logger.debug(f"capture called for multi urls: {urlinfos}")

    passed_url = []
    failed_url = []

    if not urlinfos or len(urlinfos) < 2:
        raise ValueError("urls must contain at least two URLs.")

    tasks = []
    for urlinfo in urlinfos:
        tasks.append(capture_one(urlinfo))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for urlinfo, result in zip(urlinfos, results):
        if isinstance(result, Exception):
            _logger.error(f"Error occurred while capturing {urlinfo.url}: {result}")
            failed_url.append(urlinfo)
        elif result:
            passed_url.append(urlinfo)
        else:
            failed_url.append(urlinfo)

    return passed_url, failed_url
