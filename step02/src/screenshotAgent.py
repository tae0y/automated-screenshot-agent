# uvicorn src.screenshotAgent:app --reload --port 9910

import os
import glob

from contextlib import asynccontextmanager
from fastapi import FastAPI, Body, Query

from src.agent_workflow import AgentWorkflow
from src.capture import capture_all, capture_one
from src.config import ConfigManager
from src.logger import get_logger
from src.kernel_agent import KernelAgent
from src.models import (
    ScreenshotGetResponse,
    ScreenshotGetResultData,
    ScreenshotPostRequest,
    ScreenshotPostResponse,
    ScreenshotPostResultData,
    MCPScreenshotPostRequest,
    MCPScreenshotPostResponse,
    ResultCode,
)


_config = ConfigManager()
_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app):
    # Startup logic
    banner_path = os.path.join(os.path.dirname(__file__), "banner.txt")
    with open(banner_path, encoding="utf-8") as f:
        banner = f.read()
    _logger.info(banner)
    yield
    # Shutdown logic
    _logger.info("\n\nAutomated Screenshot Agent is shutting down...\n\n")


app = FastAPI(lifespan=lifespan)
agent = KernelAgent()
agent_workflow = AgentWorkflow()


@app.get("/api/v1/predefined/screenshot", response_model=ScreenshotGetResponse)
async def get_screenshot(systemNm: str = Query(None)):
    """
    Get Screenshot
    - param
        - systemNm: str (query param, required)
    - return
        - ScreenshotResponse
    """
    _logger.info(f"GET /screenshot called with systemNm={systemNm}")
    # 파라미터 검증
    if not systemNm:
        return ScreenshotGetResponse(
            resultCd=ResultCode.INTERNAL_ERROR,
            resultMsg="systemNm query parameter is required.",
            data=None
        )

    # config에서 해당 시스템 정보 조회
    urlinfo = next((u for u in _config.URLS if u.name == systemNm), None)
    if not urlinfo:
        return ScreenshotGetResponse(
            resultCd=ResultCode.INTERNAL_ERROR,
            resultMsg=f"No URLs found for systemNm={systemNm}",
            data=None
        )

    # 스크린샷 파일 경로 탐색
    save_path = _config.SAVE_PATH
    pattern = os.path.join(save_path, f"{systemNm}-*.png")
    files = glob.glob(pattern)
    if not files:
        return ScreenshotGetResponse(
            resultCd=ResultCode.INTERNAL_ERROR,
            resultMsg=f"No screenshot found for systemNm={systemNm}",
            data=None
        )
    # 최신 파일 선택
    latest_file = max(files, key=os.path.getctime)

    # 접근 가능한 경로 반환
    # TODO: 저장경로를 난수화해서 반환하기
    static_prefix = "/static/screenshots/"
    image_name = os.path.basename(latest_file)
    image_path = static_prefix + image_name

    # 결과 데이터 생성
    result_data = ScreenshotGetResultData(
        systemNm=systemNm,
        imagePath=image_path
    )
    return ScreenshotGetResponse(
        resultCd=ResultCode.SUCCESS,
        resultMsg="Success",
        data=result_data
    )


@app.post("/api/v1/predefined/screenshot", response_model=ScreenshotPostResponse)
async def post_screenshot(request: ScreenshotPostRequest = Body(...)):
    """
    Post Screenshot
    - param
        - request: ScreenshotRequest
        - if not provided, all URLs will be processed
    - return
        - ScreenshotResponse
        
    This feature is based on the paper: LLM-Guided Scenario-based GUI Testing (Jun 2025)
    """
    _logger.info(f"POST /screenshot called with request={request}")

    if not request.systemNm:
        _logger.debug("No systemNm provided, processing all URLs.")
        requested_urlinfos = _config.URLS
        passed_urlinfos, failed_urlinfos = await capture_all(
            requested_urlinfos
        )
    else:
        _logger.debug(f"Processing URLs for systemNm={request.systemNm}.")
        requested_urlinfo = next(
            (u for u in _config.URLS if u.name == request.systemNm), None
        )
        if not requested_urlinfo:
            raise ValueError(f"No URLs found for systemNm={request.systemNm}")
        is_success = await capture_one(requested_urlinfo)
        requested_urlinfos = [requested_urlinfo]
        passed_urlinfos = [requested_urlinfo] if is_success else []
        failed_urlinfos = [] if is_success else [requested_urlinfo]

    result_data = ScreenshotPostResultData(
        requestedUrls=requested_urlinfos,
        passedUrls=passed_urlinfos,
        failedUrls=failed_urlinfos
    )
    return ScreenshotPostResponse(
        resultCd=ResultCode.SUCCESS,
        resultMsg="Success",
        data=result_data
    )


@app.post("/api/v1/mcp/screenshot", response_model=MCPScreenshotPostResponse)
async def post_mcp_screenshot(request: MCPScreenshotPostRequest = Body(...)):
    """
    Post Screenshot

    - param
        - request: MCPScreenshotPostRequest
    - return
        - ScreenshotResponse
    """
    _logger.info(f"POST /screenshot called with request={request}")

    if not request.prompt:
        _logger.error("Prompt not provided.")
        raise ValueError("Prompt is required for MCP screenshot request.")
    
    # TODO: implement MCP screenshot capture
    response = await agent.get_response(messages=request.prompt)
    _logger.debug(f"Response from agent: {str(response)}")
    result_data = getattr(response, "content", response)
    return MCPScreenshotPostResponse(
        resultCd=ResultCode.SUCCESS,
        resultMsg="Success",
        data=result_data
    )


@app.post("/api/v1/agents/screenshot", response_model=MCPScreenshotPostResponse)
async def post_mcp_screenshot(request: MCPScreenshotPostRequest = Body(...)):
    """
    Post Screenshot

    - param
        - request: MCPScreenshotPostRequest
    - return
        - ScreenshotResponse
    """
    _logger.info(f"POST /screenshot called with request={request}")

    if not request.prompt:
        _logger.error("Prompt not provided.")
        raise ValueError("Prompt is required for MCP screenshot request.")
    
    # TODO: implement Multi Agents screenshot capture
    response = await agent_workflow.get_response(messages=request.prompt)
    _logger.debug(f"Response from agent_workflow: {str(response)}")
    result_data = getattr(response, "content", response)
    return MCPScreenshotPostResponse(
        resultCd=ResultCode.SUCCESS,
        resultMsg="Success",
        data=result_data
    )
