from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class UIComponent(BaseModel):
    type: str = Field(..., description="button | link | nav | card | modal | text | img ...")
    text: Optional[str] = None
    bbox_norm: List[float] = Field(..., min_length=4, max_length=4, description="[x,y,w,h] in 0..1000")
    visible: bool = True

class OutputJSON(BaseModel):
    site_url: str
    crawl_ts: str
    ui_components: List[UIComponent]
    layout_state: Dict[str, str]
    data_content: Dict[str, str]
    browser_console_errors: List[str]
    error_count: int
    model: str
    latency_ms: int
