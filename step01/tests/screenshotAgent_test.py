# MCP screenshot 엔드포인트 테스트
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient
from src.screenshotAgent import app
import tempfile
import os
from src.models import UrlInfo
from src.config import ConfigManager
import httpx

# 테스트용 상수
INVALID_SYSTEM_NM = None
NONEXISTENT_SYSTEM_NM = "NotExist"
SUCCESS_RESULT_CD = 100
ERROR_RESULT_CD = 910

client = TestClient(app)


@pytest.mark.parametrize(
    "systemNm,expected_cd,expected_msg",
    [
        (
            INVALID_SYSTEM_NM,
            ERROR_RESULT_CD,
            "systemNm query parameter is required"
        ),
    ]
)
def test_given_invalid_systemNm_when_get_screenshot_invoked_then_should_return_error(
    systemNm, expected_cd, expected_msg
):
    response = client.get("/api/v1/predefined/screenshot")
    assert response.status_code == 200
    assert response.json()["resultCd"] == expected_cd
    assert expected_msg in response.json()["resultMsg"]


@pytest.mark.parametrize(
    "systemNm,expected_cd,expected_msg",
    [
        (NONEXISTENT_SYSTEM_NM, ERROR_RESULT_CD, "No URLs found for systemNm"),
    ]
)
def test_given_nonexistent_systemNm_when_get_screenshot_invoked_then_should_return_error(
    systemNm, expected_cd, expected_msg
):
    response = client.get(f"/api/v1/predefined/screenshot?systemNm={systemNm}")
    assert response.status_code == 200
    assert response.json()["resultCd"] == expected_cd
    assert expected_msg in response.json()["resultMsg"]


def test_given_valid_systemNm_when_get_screenshot_invoked_then_should_return_success(
    monkeypatch
):
    with tempfile.TemporaryDirectory() as tmpdir:
        systemNm = "TestSystem"
        # 테스트용 스크린샷 파일 생성
        image_name = f"{systemNm}-20251026-000000.png"
        image_path = os.path.join(tmpdir, image_name)
        with open(image_path, "wb") as f:
            f.write(b"fake image data")
        # monkeypatch로 URLS, SAVE_PATH 주입
        monkeypatch.setattr(
            ConfigManager,
            "URLS",
            [UrlInfo(name=systemNm, url="http://example.com")],
        )
        monkeypatch.setattr(ConfigManager, "SAVE_PATH", tmpdir)
        response = client.get(f"/api/v1/predefined/screenshot?systemNm={systemNm}")
        assert response.status_code == 200
        assert response.json()["resultCd"] == SUCCESS_RESULT_CD
        assert "imagePath" in response.json()["data"]


@pytest.mark.parametrize(
    "payload,expected_cd",
    [
        ({}, SUCCESS_RESULT_CD),
    ]
)
def test_given_invalid_systemNm_when_post_screenshot_invoked_then_should_return_success(
    payload, expected_cd
):
    response = client.post("/api/v1/predefined/screenshot", json=payload)
    assert response.status_code == 200
    assert response.json()["resultCd"] == expected_cd


def test_given_valid_systemNm_when_post_screenshot_invoked_then_should_return_success(
    monkeypatch
):
    systemNm = "TestSystem"
    monkeypatch.setattr(
        ConfigManager,
        "URLS",
        [UrlInfo(name=systemNm, url="https://example.com")],
    )
    response = client.post("/api/v1/predefined/screenshot", json={"systemNm": systemNm})
    assert response.status_code == 200
    assert response.json()["resultCd"] == SUCCESS_RESULT_CD


# 통합 테스트: 실제 서버에 요청
@pytest.mark.asyncio
async def test_integration_get_openapi():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9910/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()


@pytest.mark.asyncio
async def test_integration_get_screenshot_invalid_systemNm():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9910/api/v1/predefined/screenshot")
        assert response.status_code == 200
        data = response.json()
        assert data["resultCd"] == ERROR_RESULT_CD
        assert "systemNm query parameter is required" in data["resultMsg"]


def test_given_no_prompt_when_post_mcp_screenshot_then_should_return_error():
    response = client.post('/api/v1/mcp/screenshot', json={})
    assert response.status_code in (422, 500)


@patch('src.screenshotAgent.agent')
def test_given_valid_prompt_when_post_mcp_screenshot_then_should_return_success(mock_agent):
    class DummyResponse:
        def __init__(self, content):
            self.content = content
    mock_agent.get_response = AsyncMock(return_value=DummyResponse('result'))
    response = client.post('/api/v1/mcp/screenshot', json={'prompt': 'test'})
    assert response.status_code == 200
    assert response.json()['resultCd'] == SUCCESS_RESULT_CD
    assert response.json()['data'] == 'result'
