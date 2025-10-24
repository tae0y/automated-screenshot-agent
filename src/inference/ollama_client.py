
import base64, json, httpx, time
from tenacity import retry, stop_after_attempt, wait_fixed
from src.config import OLLAMA_URL
from src.inference.schema import OutputJSON

def _b64(png: bytes) -> str:
    return base64.b64encode(png).decode()

PROMPT_TMPL = """You are a strict JSON generator.
Task: Given a webpage screenshot and its cleaned markdown, extract:
- ui_components: list of objects {{type, text, bbox_norm[4], visible}}
- layout_state: key->value summary of layout relations
- data_content: key field->value summaries
- browser_console_errors: []
- error_count: integer
Rules:
- bbox_norm is normalized to 0-1000 relative to full screenshot size.
- Respond with ONLY JSON that matches this schema: {schema}
Cleaned Markdown:
```

{md}

```"""

@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
def infer_ollama(model: str, png_full: bytes, md: str) -> OutputJSON:
    schema_str = OutputJSON.model_json_schema()
    prompt = PROMPT_TMPL.format(schema=json.dumps(schema_str), md=md)
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [_b64(png_full)],
        "options": {"temperature": 0},
        "stream": False
    }
    t0 = time.time()
    with httpx.Client(timeout=90) as cx:
        r = cx.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        out = r.json()["response"]
    latency = int((time.time() - t0) * 1000)
    j = json.loads(out)
    j["model"] = model
    j["latency_ms"] = latency
    return OutputJSON(**j)
