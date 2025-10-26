import pytest
from pydantic import ValidationError
from src.models import UrlInfo, ScreenshotGetResultData, ScreenshotPostResultData, ResultCode

VALID_NAME = "Google"
VALID_URL = "https://google.com"
VALID_NAME2 = "Naver"
VALID_URL2 = "https://naver.com"
VALID_IMAGE_PATH = "/tmp/test.png"
VALID_SYSTEM_NM = "TestSystem"


@pytest.mark.parametrize("name,url", [
    (None, VALID_URL),
    (VALID_NAME, None),
    ("", VALID_URL),
    (VALID_NAME, ""),
])
def test_given_urlinfo_none_or_blank(name, url):
    # None은 허용, 공백 문자열은 예외 발생
    if name == "" or url == "":
        with pytest.raises(ValidationError):
            UrlInfo(name=name, url=url)
    else:
        urlinfo = UrlInfo(name=name, url=url)
        assert urlinfo.name == name
        assert urlinfo.url == url


@pytest.mark.parametrize("name,url", [
    (VALID_NAME, VALID_URL),
    (VALID_NAME2, VALID_URL2),
])
def test_given_valid_urlinfo_when_created_then_should_succeed(name, url):
    urlinfo = UrlInfo(name=name, url=url)
    assert urlinfo.name == name
    assert urlinfo.url == url


@pytest.mark.parametrize("systemNm,imagePath", [
    (None, VALID_IMAGE_PATH),
    (VALID_SYSTEM_NM, None),
    ("", VALID_IMAGE_PATH),
    (VALID_SYSTEM_NM, ""),
])
def test_given_screenshotgetresultdata_none_or_blank(systemNm, imagePath):
    # None은 허용, 공백 문자열은 예외 발생
    if systemNm == "" or imagePath == "":
        with pytest.raises(ValidationError):
            ScreenshotGetResultData(systemNm=systemNm, imagePath=imagePath)
    else:
        data = ScreenshotGetResultData(systemNm=systemNm, imagePath=imagePath)
        assert data.systemNm == systemNm
        assert data.imagePath == imagePath


@pytest.mark.parametrize("systemNm,imagePath", [
    (VALID_SYSTEM_NM, VALID_IMAGE_PATH),
    ("AnotherSystem", "/tmp/another.png"),
])
def test_given_valid_screenshotgetresultdata_when_created_then_should_succeed(systemNm, imagePath):
    data = ScreenshotGetResultData(systemNm=systemNm, imagePath=imagePath)
    assert data.systemNm == systemNm
    assert data.imagePath == imagePath


@pytest.mark.parametrize("requestedUrls,passedUrls,failedUrls", [
    ([{"name": "", "url": VALID_URL}], [], []),
    ([{"name": VALID_NAME, "url": ""}], [], []),
    ([{"name": None, "url": VALID_URL}], [], []),
    ([{"name": VALID_NAME, "url": None}], [], []),
    (None, [], []),
    ([], None, []),
    ([], [], None),
])
def test_given_screenshotpostresultdata_none_or_blank(requestedUrls, passedUrls, failedUrls):
    # None은 허용, 리스트 내 공백 문자열은 예외 발생
    def has_blank_urlinfo(lst):
        if lst is None:
            return False
        return any((x is not None and (x.get("name", None) == "" or x.get("url", None) == "")) for x in lst)

    def to_urlinfo_list(lst):
        if lst is None:
            return None
        result = []
        for x in lst:
            try:
                result.append(UrlInfo(**x) if isinstance(x, dict) else x)
            except ValidationError:
                result.append(x)  # ValidationError 발생 시 그대로 dict로 남김
        return result

    if requestedUrls is None or passedUrls is None or failedUrls is None or has_blank_urlinfo(requestedUrls):
        with pytest.raises(ValidationError):
            requestedObjs = []
            if requestedUrls is not None:
                for x in requestedUrls:
                    requestedObjs.append(UrlInfo(**x))
            passedObjs = []
            if passedUrls is not None:
                for x in passedUrls:
                    passedObjs.append(UrlInfo(**x))
            failedObjs = []
            if failedUrls is not None:
                for x in failedUrls:
                    failedObjs.append(UrlInfo(**x))
            ScreenshotPostResultData(requestedUrls=requestedObjs if requestedUrls is not None else None,
                                    passedUrls=passedObjs if passedUrls is not None else None,
                                    failedUrls=failedObjs if failedUrls is not None else None)
    else:
        requestedObjs = to_urlinfo_list(requestedUrls)
        passedObjs = to_urlinfo_list(passedUrls)
        failedObjs = to_urlinfo_list(failedUrls)
        data = ScreenshotPostResultData(requestedUrls=requestedObjs, passedUrls=passedObjs, failedUrls=failedObjs)
        assert data.requestedUrls == requestedObjs
        assert data.passedUrls == passedObjs
        assert data.failedUrls == failedObjs


@pytest.mark.parametrize("requestedUrls,passedUrls,failedUrls", [
    ([UrlInfo(name=VALID_NAME, url=VALID_URL), UrlInfo(name=VALID_NAME2, url=VALID_URL2)],
     [UrlInfo(name=VALID_NAME, url=VALID_URL)],
     [UrlInfo(name=VALID_NAME2, url=VALID_URL2)]),
])
def test_given_valid_screenshotpostresultdata_when_created_then_should_succeed(requestedUrls, passedUrls, failedUrls):
    data = ScreenshotPostResultData(
        requestedUrls=requestedUrls,
        passedUrls=passedUrls,
        failedUrls=failedUrls
    )
    assert len(data.requestedUrls) == len(requestedUrls)
    assert len(data.passedUrls) == len(passedUrls)
    assert len(data.failedUrls) == len(failedUrls)


def test_given_resultcode_enum_when_accessed_then_should_return_expected_values():
    assert ResultCode.SUCCESS.value == 100
    assert ResultCode.FAIL.value == 900
    assert ResultCode.INTERNAL_ERROR.value == 910
    assert ResultCode.EXTERNAL_ERROR.value == 920
