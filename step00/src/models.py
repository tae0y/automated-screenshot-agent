from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


# Custom Types
class UrlInfo(BaseModel):
    """
    URL Information Model
    """
    name: str
    url: str


class ScreenshotGetResultData(BaseModel):
    systemNm: str
    imagePath: str


class ScreenshotPostResultData(BaseModel):
    requestedUrls: List[UrlInfo]
    passedUrls: List[UrlInfo]
    failedUrls: List[UrlInfo]

    def __init__(self, requestedUrls, passedUrls, failedUrls, **kwargs):
        requestedUrls = [requestedUrls] if not isinstance(requestedUrls, list) else requestedUrls
        passedUrls = [passedUrls] if not isinstance(passedUrls, list) else passedUrls
        failedUrls = [failedUrls] if not isinstance(failedUrls, list) else failedUrls
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


# Custom Base Models
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


# Inherited Models
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
