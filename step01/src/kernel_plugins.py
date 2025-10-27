# Created by blackwhite084 in mcp, released under Apache 2.0
# Modified by tae0y in semantic kernel adaptation, and added customizations

import base64
import os
import time
import uuid

from bs4 import BeautifulSoup

from typing import Annotated, Optional

from playwright.async_api import async_playwright

from src.config import ConfigManager
from src.logger import get_logger
from semantic_kernel.functions import kernel_function

_logger = get_logger(__name__)
_config = ConfigManager()


class WebNavigationPlugin:
    def __init__(self):
        self._sessions = {}
        self._playwright = None

    @kernel_function(description="Create a new browser session")
    async def new_session(self, url: Optional[str] = None) -> Annotated[str, "Session creation result"]:
        """
        Playwright 브라우저 세션을 생성하고, 필요시 URL로 이동합니다.
        """
        _logger.info("Creating new browser session.")
        try:
            self._playwright = await async_playwright().start()
            browser = await self._playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = {"browser": browser, "page": page}
            if url:
                if not url.startswith("http://") and not url.startswith("https://"):
                    url = "https://" + url
                await page.goto(url)
            return f"Session created: {session_id}"
        except Exception as e:
            return f"Session creation failed: {e}"

    @kernel_function(description="Navigate to a URL")
    async def navigate(self, url: str) -> Annotated[str, "Navigation result"]:
        """
        현재 세션의 페이지에서 URL로 이동합니다.
        """
        _logger.info(f"Navigating to URL: {url}")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            await page.goto(url)
            return f"Navigated to {url}"
        except Exception as e:
            return f"Navigation failed: {e}"

    @kernel_function(description="Take a screenshot")
    async def screenshot(self, name: str, selector: Optional[str] = None) -> Annotated[str, "Base64 encoded image"]:
        """
        전체 페이지 또는 특정 selector의 스크린샷을 base64로 반환합니다.
        """
        _logger.info(f"Taking screenshot: {name}, selector: {selector}")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            save_path = _config.SAVE_PATH
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            file_path = f"{save_path}/{name}-{timestamp}.png"
            if selector:
                element = page.locator(selector)
                await element.screenshot(path=file_path)
            else:
                await page.screenshot(path=file_path, full_page=True)
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            # os.remove(file_path)
            # return encoded_string
            return f"Screenshot saved and encoded: {file_path}"
        except Exception as e:
            return f"Screenshot failed: {e}"

    @kernel_function(description="Click an element by selector")
    async def click(self, selector: str) -> Annotated[str, "Click result"]:
        """
        지정된 셀렉터의 요소를 클릭합니다.
        """
        _logger.info(f"Clicking element with selector: {selector}")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            await page.locator(selector).click()
            return f"Clicked element with selector {selector}"
        except Exception as e:
            return f"Click failed: {e}"

    @kernel_function(description="Fill an input field")
    async def fill(self, selector: str, value: str) -> Annotated[str, "Fill result"]:
        """
        지정된 셀렉터의 입력 필드를 채웁니다.
        """
        _logger.info(f"Filling element with selector: {selector} with value: {value}")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            await page.locator(selector).fill(value)
            return f"Filled element with selector {selector} with value {value}"
        except Exception as e:
            return f"Fill failed: {e}"

    @kernel_function(description="Evaluate JS in browser")
    async def evaluate(self, script: str) -> Annotated[str, "Evaluation result"]:
        """
        브라우저에서 JavaScript 코드를 실행합니다.
        """
        _logger.info(f"Evaluating script: {script}")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            result = await page.evaluate(script)
            return f"Evaluated script, result: {result}"
        except Exception as e:
            return f"Evaluate failed: {e}"

    @kernel_function(description="Click element by text")
    async def click_text(self, text: str) -> Annotated[str, "Click result"]:
        """
        지정된 텍스트를 포함하는 요소를 클릭합니다.
        """
        _logger.info(f"Clicking element with text: {text}")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            await page.locator(f"text={text}").nth(0).click()
            return f"Clicked element with text {text}"
        except Exception as e:
            return f"Click by text failed: {e}"

    @kernel_function(description="Get text content of all elements")
    async def get_text_content(self) -> Annotated[str, "Text content"]:
        """
        현재 페이지의 모든 텍스트 콘텐츠를 가져옵니다.
        """
        _logger.info("Getting text content of all elements.")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            # 주요 텍스트 추출 (body 기준)
            text_contents = await page.locator('body').all_inner_texts()
            return f"Text content of body: {text_contents}"
        except Exception as e:
            return f"Get text content failed: {e}"

    @kernel_function(description="Get HTML content of element")
    async def get_html_content(self, selector: str) -> Annotated[str, "HTML content"]:
        """
        지정된 셀렉터의 요소 HTML 콘텐츠를 가져옵니다.
        """
        _logger.info(f"Getting HTML content of element with selector: {selector}")
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            html_content = await page.locator(selector).inner_html()
            return f"HTML content of element with selector {selector}: {html_content}"
        except Exception as e:
            return f"Get HTML content failed: {e}"

    @kernel_function(description="Get visible and cleaned HTML from a URL (body only)")
    async def get_visible_html(self, url: str) -> Annotated[str, "Visible HTML content"]:
        """
        주어진 URL에서 보이는 HTML 콘텐츠를 가져옵니다.
        """
        _logger.info(f"Getting visible HTML from URL: {url}")
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            visible_html = await page.evaluate("document.body.innerHTML")
            await browser.close()
            await playwright.stop()
            cleaned_html = await self._clean_html(visible_html)
            _logger.debug(f"Visible HTML fetched and cleaned. before length: {len(visible_html)}, after length: {len(cleaned_html)}")
            return cleaned_html
        except Exception as e:
            return f"Failed to get visible HTML: {e}"

    # TODO: custom.py에 정의된 커스텀 login, logout 함수를 호출, 컨텍스트를 안전하게 공유하기
    # def login():
    # def logout():
    # def save_context():
    # def load_context():
    # def save_screenshot():
    # def get_url_from_system_name():


    async def _clean_html(self, html: str) -> Annotated[str, "Cleaned HTML content"]:
        try:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["span", "style", "script", "noscript", "meta", "link"]):
                tag.decompose()
            cleaned_html = str(soup)
            return cleaned_html
        except Exception as e:
            return f"Failed to clean HTML: {e}"
