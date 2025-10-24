
from src.storage.db import get_conn
from src.inference.schema import OutputJSON
import json

def insert_record(out: OutputJSON, png_path: str, html_path: str):
    with get_conn() as conn:
        conn.execute(
          """INSERT INTO web_audit(
            site_url,crawl_ts,model,latency_ms,ui_components,layout_state,data_content,
            browser_console_errors,error_count,art_html_path,art_screenshot_path
          ) VALUES (%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s,%s)""",
          (
            out.site_url, out.crawl_ts, out.model, out.latency_ms,
            json.dumps([c.model_dump() for c in out.ui_components]),
            json.dumps(out.layout_state),
            json.dumps(out.data_content),
            json.dumps(out.browser_console_errors),
            out.error_count, html_path, png_path
          )
        )
