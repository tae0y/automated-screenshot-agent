import os
from dotenv import load_dotenv
load_dotenv()


PG_DSN = os.getenv("PG_DSN", "postgresql://user:pass@localhost:5432/webaudit")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
OUTDIR = os.getenv("OUTDIR", "data")
VIEWPORT = {"width": 1280, "height": 2000}
TIMEOUT_S = 10
RETRIES = 3
