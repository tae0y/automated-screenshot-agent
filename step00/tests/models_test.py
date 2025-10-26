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
def test_given_invalid_urlinfo_when_created_then_should_throw(name, url):
    with pytest.raises(ValidationError):
        UrlInfo(name=name, url=url)


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
def test_given_invalid_screenshotgetresultdata_when_created_then_should_throw(systemNm, imagePath):
    with pytest.raises(ValidationError):
        ScreenshotGetResultData(systemNm=systemNm, imagePath=imagePath)


@pytest.mark.parametrize("systemNm,imagePath", [
    (VALID_SYSTEM_NM, VALID_IMAGE_PATH),
    ("AnotherSystem", "/tmp/another.png"),
])
def test_given_valid_screenshotgetresultdata_when_created_then_should_succeed(systemNm, imagePath):
    data = ScreenshotGetResultData(systemNm=systemNm, imagePath=imagePath)
    assert data.systemNm == systemNm
    assert data.imagePath == imagePath


@pytest.mark.parametrize("requestedUrls,passedUrls,failedUrls", [
    (None, [], []),
    ([], None, []),
    ([], [], None),
])
def test_given_invalid_screenshotpostresultdata_when_created_then_should_throw(requestedUrls, passedUrls, failedUrls):
    with pytest.raises(ValidationError):
        ScreenshotPostResultData(requestedUrls=requestedUrls, passedUrls=passedUrls, failedUrls=failedUrls)


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
