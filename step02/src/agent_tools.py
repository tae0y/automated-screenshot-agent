# Created by blackwhite084 in mcp, released under Apache 2.0
# Modified by tae0y in agent framework adaptation, and added customizations

import base64
import os
import time
import uuid

from bs4 import BeautifulSoup

from typing import Annotated, Optional

from agent_framework._tools import ai_function
from playwright.async_api import async_playwright
from pydantic import Field

from src.config import ConfigManager
from src.logger import get_logger
from semantic_kernel.functions import kernel_function

_logger = get_logger(__name__)
_config = ConfigManager()
_sessions = {}
_playwright = None

@ai_function(name="new_session", description="Create a new browser session")
async def new_session(url: Annotated[str, Field(description="The URL to navigate to after creating the session")]) -> Annotated[str, "Session creation result"]:
    """
    Playwright 브라우저 세션을 생성하고, 필요시 URL로 이동합니다.
    """
    _logger.info(f"[TOOLS] Creating new browser session with URL: {url}")
    try:
        global _playwright
        _playwright = await async_playwright().start()
        # TODO: headless=False는 데모용
        browser = await _playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {"browser": browser, "page": page}
        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            await page.goto(url)
        return f"Session created: {session_id}"
    except Exception as e:
        return f"Session creation failed: {e}"

@ai_function(name="navigate", description="Navigate to a URL")
async def navigate(
    url: Annotated[str, Field(description="The URL to navigate to after creating the session")]
) -> Annotated[str, "Navigation result"]:
    """
    현재 세션의 페이지에서 URL로 이동합니다.
    """
    _logger.info(f"[TOOLS] Navigating to URL: {url}")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        await page.goto(url)
        return f"Navigated to {url}"
    except Exception as e:
        return f"Navigation failed: {e}"

@ai_function(name="screenshot", description="Take a screenshot")
async def screenshot(
    name: Annotated[str, Field(description="The name of the screenshot")],
    selector: Annotated[str, Field(description="The selector of the element to screenshot")] = None,
) -> Annotated[str, "Base64 encoded image"]:
    """
    전체 페이지 또는 특정 selector의 스크린샷을 base64로 반환합니다.
    """
    _logger.info(f"[TOOLS] Taking screenshot: {name}, selector: {selector}")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
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

@ai_function(name="click", description="Click an element by selector")
async def click(
    selector: Annotated[str, Field(description="The selector of the element to click")]
) -> Annotated[str, "Click result"]:
    """
    지정된 셀렉터의 요소를 클릭합니다.
    """
    _logger.info(f"[TOOLS] Clicking element with selector: {selector}")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        await page.locator(selector).click()
        return f"Clicked element with selector {selector}"
    except Exception as e:
        return f"Click failed: {e}"

@ai_function(name="fill", description="Fill an input field")
async def fill(
    selector: Annotated[str, Field(description="The selector of the element to fill")],
    value: Annotated[str, Field(description="The value to fill the input field with")]
) -> Annotated[str, "Fill result"]:
    """
    지정된 셀렉터의 입력 필드를 채웁니다.
    """
    _logger.info(f"[TOOLS] Filling element with selector: {selector} with value: {value}")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        await page.locator(selector).fill(value)
        return f"Filled element with selector {selector} with value {value}"
    except Exception as e:
        return f"Fill failed: {e}"

@ai_function(name="evaluate", description="Evaluate JS in browser")
async def evaluate(
    script: Annotated[str, Field(description="The JavaScript code to evaluate")]
) -> Annotated[str, "Evaluation result"]:
    """
    브라우저에서 JavaScript 코드를 실행합니다.
    """
    _logger.info(f"[TOOLS] Evaluating script: {script}")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        result = await page.evaluate(script)
        return f"Evaluated script, result: {result}"
    except Exception as e:
        return f"Evaluate failed: {e}"

@ai_function(name="click_text", description="Click element by text")
async def click_text(
    text: Annotated[str, Field(description="The text of the element to click")]
) -> Annotated[str, "Click result"]:
    """
    지정된 텍스트를 포함하는 요소를 클릭합니다.
    """
    _logger.info(f"[TOOLS] Clicking element with text: {text}")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        await page.locator(f"text={text}").nth(0).click()
        return f"Clicked element with text {text}"
    except Exception as e:
        return f"Click by text failed: {e}"

@ai_function(name="get_text_content", description="Get text content of all elements")
async def get_text_content() -> Annotated[str, "Text content"]:
    """
    현재 페이지의 모든 텍스트 콘텐츠를 가져옵니다.
    """
    _logger.info(f"[TOOLS] Getting text content of all elements.")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        # 주요 텍스트 추출 (body 기준)
        text_contents = await page.locator('body').all_inner_texts()
        return f"Text content of body: {text_contents}"
    except Exception as e:
        return f"Get text content failed: {e}"

@ai_function(name="get_html_content", description="Get HTML content of element")
async def get_html_content(
    selector: Annotated[str, Field(description="The selector of the element to get HTML content from")]
) -> Annotated[str, "HTML content"]:
    """
    지정된 셀렉터의 요소 HTML 콘텐츠를 가져옵니다.
    """
    _logger.info(f"[TOOLS] Getting HTML content of element with selector: {selector}")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        html_content = await page.locator(selector).inner_html()
        cleaned_html = await _clean_html(html_content)
        _logger.debug(f"HTML content fetched and cleaned for selector {selector}. before length: {len(html_content)}, after length: {len(cleaned_html)}")
        return f"HTML content of element with selector {selector}: {cleaned_html}"
    except Exception as e:
        return f"Get HTML content failed: {e}"

@ai_function(name="get_visible_html", description="Get visible and cleaned HTML from the current page (body only)")
async def get_visible_html() -> Annotated[str, "Visible HTML content"]:
    """
    현재 페이지의 보이는 HTML(body) 콘텐츠를 가져옵니다.
    """
    _logger.info(f"[TOOLS] Getting visible HTML from current page.")
    if not _sessions:
        return "No active session. Please create a new session first."
    session_id = list(_sessions.keys())[-1]
    page = _sessions[session_id]["page"]
    try:
        visible_html = await page.locator("body").inner_html()
        cleaned_html = await _clean_html(visible_html)
        _logger.debug(f"Visible HTML fetched and cleaned. before length: {len(visible_html)}, after length: {len(cleaned_html)}")
        # TODO: 토큰 절약을 위해 cleaned_html 반환, 현재는 cleaned된 html에서 dom을 잘 읽지 못해 visible_html 반환
        return visible_html
    except Exception as e:
        return f"Failed to get visible HTML: {e}"

# TODO: custom.py에 정의된 커스텀 login, logout 함수를 호출, 컨텍스트를 안전하게 공유하기
# def login():
# def logout():
# def save_context():
# def load_context():
# def save_screenshot():
# def get_url_from_system_name():


async def _clean_html(html: str) -> Annotated[str, "Cleaned HTML content"]:
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["span", "style", "script", "noscript", "meta", "link"]):
            tag.decompose()
        cleaned_html = str(soup)
        return cleaned_html
    except Exception as e:
        return f"Failed to clean HTML: {e}"
