import pytest
from src.capture import is_valid_url, capture_one, capture_all
from src.models import UrlInfo
import tempfile
import os
from src.config import ConfigManager

# 테스트용 상수
VALID_URL = "https://example.com"
VALID_URL_HTTP = "http://example.com"
INVALID_URLS = [
    "", "ftp://example.com", "http:/example.com", "example.com", "http://"
]
VALID_NAME = "Test"
INVALID_NAME = "Invalid"


@pytest.mark.parametrize("url", INVALID_URLS)
def test_given_invalid_url_when_is_valid_url_invoked_then_should_return_false(
    url
):
    assert not is_valid_url(url)


@pytest.mark.parametrize("url", [VALID_URL, VALID_URL_HTTP])
def test_given_valid_url_when_is_valid_url_invoked_then_should_return_true(
    url
):
    assert is_valid_url(url)


@pytest.mark.asyncio
async def test_given_invalid_urlinfo_when_capture_one_invoked_then_should_throw(
    urlinfo_dict
):
    with pytest.raises((ValueError, Exception)):
        urlinfo = UrlInfo(**urlinfo_dict)
        await capture_one(urlinfo)


@pytest.mark.asyncio
async def test_given_invalid_urlinfos_when_capture_all_invoked_then_should_throw(
    urlinfos_dict
):
    with pytest.raises((ValueError, Exception)):
        urlinfos = [
            UrlInfo(**x) if isinstance(x, dict) else x for x in urlinfos_dict
        ]
        await capture_all(urlinfos)


@pytest.mark.asyncio
async def test_given_valid_urlinfo_when_capture_one_invoked_then_should_succeed(
):
    # 임시 저장 경로 지정
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager()
        config._config["SCREENSHOT"] = {"SAVE_PATH": tmpdir}
        urlinfo = UrlInfo(name=VALID_NAME, url=VALID_URL)
        result = await capture_one(urlinfo)
        assert result is True
        # 파일 생성 확인
        files = os.listdir(tmpdir)
        assert any(f.endswith(".png") for f in files)


@pytest.mark.asyncio
async def test_given_mixed_urlinfos_when_capture_all_invoked_then_should_return_passed_and_failed(
):
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager()
        config._config["SCREENSHOT"] = {"SAVE_PATH": tmpdir}
        valid = UrlInfo(name=VALID_NAME, url=VALID_URL)
        invalid = UrlInfo(name=INVALID_NAME, url="invalid-url")
        urlinfos = [valid, invalid]
        passed, failed = await capture_all(urlinfos)
        assert valid in passed
        assert invalid in failed
