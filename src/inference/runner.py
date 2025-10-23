from .ollama_client import infer_ollama
from .azure_client import infer_azure
from .schema import OutputJSON

LOCAL_MODELS = ["moondream", "granite3.2-vision:2b", "llava:7b"]

def run_inference(png: bytes, md: str) -> OutputJSON:
    last_err = None
    for m in LOCAL_MODELS:
        try:
            return infer_ollama(m, png, md)
        except Exception as e:
            last_err = e
    return infer_azure(png, md)
