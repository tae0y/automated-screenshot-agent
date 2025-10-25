# uvicorn src.screenshotAgent:app --reload --port 9910

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from typing import Optional

from src.config import ConfigManager
from src.logger import get_logger


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


@app.get("/screenshot")
def get_screenshot(systemNm: Optional[str] = Query(None)):
    _logger.info(f"GET /screenshot called with systemNm={systemNm}")
    urls = [u for u in _config.URLS if (systemNm is None or u["name"] == systemNm)]
    # 실제 캡처 로직은 capture(urls)로 연결
    return {"urls": urls, "method": "GET"}


@app.post("/screenshot")
def post_screenshot(systemNm: Optional[str] = Query(None)):
    _logger.info(f"POST /screenshot called with systemNm={systemNm}")
    urls = [u for u in _config.URLS if (systemNm is None or u["name"] == systemNm)]
    # 실제 캡처 로직은 capture(urls)로 연결
    return {"urls": urls, "method": "POST"}
