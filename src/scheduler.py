import asyncio, os, json, datetime, hashlib
from src.urls import URLS
from src.collector.browser import render
from src.collector.screenshot import naive_sections_from_full
from src.preprocess.clean import clean_html_to_md
from src.inference.runner import run_inference
from src.storage.sink import insert_record

OUTDIR = "data"

async def process_one(url: str):
    # 렌더링 및 수집
    r = await render(url)
    ts = datetime.datetime.utcnow().isoformat()
    day = datetime.datetime.utcnow().strftime("%Y%m%d")
    h = hashlib.sha1(url.encode()).hexdigest()[:8]

    dstdir = os.path.join(OUTDIR, "raw", day, h)
    os.makedirs(dstdir, exist_ok=True)

    png_path = os.path.join(dstdir, "full.png")
    with open(png_path, "wb") as f:
        f.write(r["png_bytes"])
    html_path = os.path.join(dstdir, "page.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(r["html"])

    # 정제 텍스트
    md = clean_html_to_md(r["html"])
    # 섹션 분할 메타만 사용(모델 입력은 전체 스크린샷)
    sec = naive_sections_from_full(r["png_bytes"])
    _w, _h = sec["w"], sec["h"]

    # 추론
    out = run_inference(r["png_bytes"], md)

    # 콘솔 오류 반영
    errs = [m["text"] for m in r["console"] if m["type"] == "error"]
    out.browser_console_errors = errs
    out.error_count = len(errs)

    # 메타 채우기
    out.site_url = url
    out.crawl_ts = ts

    # 저장
    insert_record(out, png_path, html_path)
    return out

async def run_all():
    # 순차 수행: 8GB 환경 안정성 우선
    results = []
    for u in URLS:
        try:
            results.append(await process_one(u))
        except Exception as e:
            results.append({"site_url": u, "error": str(e)})
    return results

def main():
    asyncio.run(run_all())

if __name__ == "__main__":
    main()
