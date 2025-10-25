# uvicorn src.screenshotAgent:app --reload --port 9910

from contextlib import asynccontextmanager
from fastapi import FastAPI, Body, Query

from src.capture import capture_all, capture_one
from src.config import ConfigManager
from src.logger import get_logger
from src.models import ScreenshotRequest, ScreenshotResponse, ScreenshotResultData, ResultCode


_config = ConfigManager()
_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app):
    # Startup logic
    _logger.info("""

    ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗███████╗██╗  ██╗ ██████╗ ████████╗
    ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║██╔════╝██║  ██║██╔═══██╗╚══██╔══╝
    ███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║███████╗███████║██║   ██║   ██║
    ╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║╚════██║██╔══██║██║   ██║   ██║
    ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║███████║██║  ██║╚██████╔╝   ██║
    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝

     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║
    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║
    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║
    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝

    Now starting the Automated Screenshot Agent...
    """)
    yield
    # Shutdown logic
    _logger.info("\n\nAutomated Screenshot Agent is shutting down...\n\n")


app = FastAPI(lifespan=lifespan)


@app.get("/screenshot", response_model=ScreenshotResponse)
async def get_screenshot(systemNm: str = Query(None)):
    """
    Get Screenshot
    - param
        - systemNm: str (optional, query param)
        - if not provided, all URLs will be processed
    - return
        - ScreenshotResponse
    """
    pass


@app.post("/screenshot", response_model=ScreenshotResponse)
async def post_screenshot(request: ScreenshotRequest = Body(...)):
    """
    Post Screenshot
    - param
        - request: ScreenshotRequest
        - if not provided, all URLs will be processed
    - return
        - ScreenshotResponse
    """
    _logger.info(f"POST /screenshot called with request={request}")

    if not request.systemNm:
        _logger.debug("No systemNm provided, processing all URLs.")
        requested_urls = _config.URLS
        passed_urls, failed_urls = capture_all(requested_urls)
    else:
        _logger.debug(f"Processing URLs for systemNm={request.systemNm}.")
        requested_url = next((u.url for u in _config.URLS if u.name == request.systemNm), None)
        if not requested_url:
            raise ValueError(f"No URLs found for systemNm={request.systemNm}")
        is_success = capture_one(requested_url)
        requested_urls = [requested_url]
        passed_urls = [requested_url] if is_success else []
        failed_urls = [] if is_success else [requested_url]

    result_data = ScreenshotResultData(
        requestedUrls=requested_urls,
        passedUrls=passed_urls,
        failedUrls=failed_urls
    )
    return ScreenshotResponse(
        resultCd=ResultCode.SUCCESS,
        resultMsg="Success",
        data=result_data
    )
