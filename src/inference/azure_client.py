
import os, json, base64, time, httpx
from src.config import AZURE_ENDPOINT, AZURE_API_KEY
from src.inference.schema import OutputJSON

def infer_azure(png_full: bytes, md: str) -> OutputJSON:
    if not AZURE_ENDPOINT or not AZURE_API_KEY:
        raise RuntimeError("Azure endpoint or key not configured")
    schema = OutputJSON.model_json_schema()
    b64 = base64.b64encode(png_full).decode()
    msgs = [
      {"role": "system", "content": "You output ONLY JSON valid for the given schema."},
      {"role": "user", "content": [
        {"type": "text", "text": f"Schema:\n{json.dumps(schema)}\nCleaned Markdown:\n{md}"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
      ]}
    ]
    t0 = time.time()
    headers = {"api-key": AZURE_API_KEY, "Content-Type": "application/json"}
    with httpx.Client(timeout=90, headers=headers) as cx:
        r = cx.post(AZURE_ENDPOINT, json={"messages": msgs, "temperature": 0})
        r.raise_for_status()
        out = r.json()
    content = out["choices"][0]["message"]["content"]
    j = json.loads(content)
    j["model"] = "azure_fallback"
    j["latency_ms"] = int((time.time() - t0) * 1000)
    return OutputJSON(**j)
