from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class UrlInfo(BaseModel):
    """
    URL Information Model
    """
    name: Optional[str] = Field(None, min_length=1)
    url: Optional[str] = Field(None, min_length=1)


class ScreenshotGetResultData(BaseModel):
    systemNm: Optional[str] = Field(None, min_length=1)
    imagePath: Optional[str] = Field(None, min_length=1)


class ScreenshotPostResultData(BaseModel):
    requestedUrls: List[UrlInfo]
    passedUrls: List[UrlInfo]
    failedUrls: List[UrlInfo]

    def __init__(self, requestedUrls, passedUrls, failedUrls, **kwargs):
        requestedUrls = (
            [requestedUrls]
            if not isinstance(requestedUrls, list)
            else requestedUrls
        )
        passedUrls = (
            [passedUrls] if not isinstance(passedUrls, list) else passedUrls
        )
        failedUrls = (
            [failedUrls] if not isinstance(failedUrls, list) else failedUrls
        )
        super().__init__(
            requestedUrls=requestedUrls,
            passedUrls=passedUrls,
            failedUrls=failedUrls,
            **kwargs
        )


class ResultCode(Enum):
    SUCCESS = 100
    FAIL = 900
    INTERNAL_ERROR = 910
    EXTERNAL_ERROR = 920


class BaseRequest(BaseModel):
    """
    Base Request Model
    """
    pass


class BaseResponse(BaseModel):
    """
    Base Response Model
    """
    resultCd: ResultCode
    resultMsg: str
    data: Optional[BaseModel] = None


class ScreenshotGetResponse(BaseResponse):
    """
    Screenshot Response Model
    """
    data: Optional[ScreenshotGetResultData] = None


class ScreenshotPostRequest(BaseRequest):
    """
    Screenshot Request Model
    """
    systemNm: Optional[str] = None


class ScreenshotPostResponse(BaseResponse):
    """
    Screenshot Response Model
    """
    data: Optional[ScreenshotPostResultData] = None


class MCPScreenshotPostRequest(BaseRequest):
    """
    MCP Screenshot Request Model
    """
    prompt: str


class MCPScreenshotPostResponse(BaseResponse):
    """
    MCP Screenshot Response Model
    """
    data: Optional[ScreenshotPostResultData] = None
