from trafilatura import extract
from readability import Document
import re

def clean_html_to_md(html: str) -> str:
    try:
        main_html = Document(html).summary()
    except Exception:
        main_html = html
    md = extract(main_html, include_comments=False, output_format="markdown", favor_recall=True)
    if not md:
        md = extract(html, output_format="markdown") or ""
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md
