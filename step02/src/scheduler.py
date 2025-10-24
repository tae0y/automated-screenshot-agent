
import asyncio, os, json, datetime, hashlib
from src.urls import URLS
from src.collector.browser import render
from src.collector.screenshot import naive_sections_from_full
from src.preprocess.clean import clean_html_to_md
from src.inference.runner import run_inference
from src.storage.sink import insert_record

from src.config import OUTDIR

async def process_one(url: str):
    print(f"[INFO] Start processing: {url}")
    # 렌더링 및 수집
    try:
        print("[INFO] Rendering and collecting...")
        r = await render(url)
    except Exception as e:
        print(f"[ERROR] Rendering failed for {url}: {e}")
        raise
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

    print("[INFO] Cleaning HTML to Markdown...")
    md = clean_html_to_md(r["html"])
    # 섹션 분할 메타만 사용(모델 입력은 전체 스크린샷)
    sec = naive_sections_from_full(r["png_bytes"])
    _w, _h = sec["w"], sec["h"]

    print("[INFO] Running inference...")
    try:
        out = run_inference(r["png_bytes"], md)
    except Exception as e:
        print(f"[ERROR] Inference failed for {url}: {e}")
        raise

    # 콘솔 오류 반영
    errs = [m["text"] for m in r["console"] if m["type"] == "error"]
    out.browser_console_errors = errs
    out.error_count = len(errs)

    # 메타 채우기
    out.site_url = url
    out.crawl_ts = ts

    print("[INFO] Inserting record to storage...")
    try:
        insert_record(out, png_path, html_path)
    except Exception as e:
        print(f"[ERROR] Storage insert failed for {url}: {e}")
        raise
    print(f"[INFO] Finished processing: {url}")
    return out

async def run_all():
    # 순차 수행: 8GB 환경 안정성 우선
    results = []
    for u in URLS:
        try:
            result = await process_one(u)
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Failed to process {u}: {e}")
            results.append({"site_url": u, "error": str(e)})
        break #test
    print("[INFO] All processing complete.")
    return results

def main():
    asyncio.run(run_all())

if __name__ == "__main__":
    main()
