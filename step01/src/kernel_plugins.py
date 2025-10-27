# Created by blackwhite084 in mcp, released under Apache 2.0
# Modified by tae0y in semantic kernel adaptation, and added customizations

import base64
import os
import uuid

from typing import Annotated, Optional

from playwright.async_api import async_playwright

from semantic_kernel.functions import kernel_function


class PlaywrightPlugin:
    def __init__(self):
        self._sessions = {}
        self._playwright = None


    @kernel_function(description="Create a new browser session")
    async def new_session(self, url: Optional[str] = None) -> Annotated[str, "Session creation result"]:
        """
        Playwright 브라우저 세션을 생성하고, 필요시 URL로 이동합니다.
        """
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
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            file_path = f"{name}.png"
            if selector:
                element = page.locator(selector)
                await element.screenshot(path=file_path)
            else:
                await page.screenshot(path=file_path, full_page=True)
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            os.remove(file_path)
            return encoded_string
        except Exception as e:
            return f"Screenshot failed: {e}"


    @kernel_function(description="Click an element by selector")
    async def click(self, selector: str) -> Annotated[str, "Click result"]:
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
        if not self._sessions:
            return "No active session. Please create a new session first."
        session_id = list(self._sessions.keys())[-1]
        page = self._sessions[session_id]["page"]
        try:
            html_content = await page.locator(selector).inner_html()
            return f"HTML content of element with selector {selector}: {html_content}"
        except Exception as e:
            return f"Get HTML content failed: {e}"
