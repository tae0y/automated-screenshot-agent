
import asyncio, time
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright
from src.config import VIEWPORT, TIMEOUT_S

@asynccontextmanager
async def chromium():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True, args=["--disable-gpu"])
    try:
        yield browser
    finally:
        await browser.close()
        await pw.stop()

async def render(url: str, timeout_s: int = TIMEOUT_S):
    async with chromium() as browser:
        ctx = await browser.new_context(
            viewport=VIEWPORT,
            java_script_enabled=True,
            ignore_https_errors=True,
            locale="ko-KR"
        )
        page = await ctx.new_page()
        console_msgs = []
        page.on("console", lambda m: console_msgs.append({"type": m.type, "text": m.text()}))
        start = time.time()
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_s*1000)
            await page.wait_for_load_state("networkidle", timeout=timeout_s*1000)
        except Exception:
            await ctx.close()
            raise
        png = await page.screenshot(full_page=True, type="png")
        html = await page.content()
        end = time.time()
        await ctx.close()
        return {
          "status": resp.status if resp else None,
          "elapsed_s": end - start,
          "png_bytes": png,
          "html": html,
          "console": console_msgs,
        }
