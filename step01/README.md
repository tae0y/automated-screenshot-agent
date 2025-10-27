# STEP 01 : Playwright MCP를 사용해 자동점검

- 당초 프로세스: 스케줄 작업으로 스크린샷, 당직자는 확인후 보고(5분 내외)
- 변경 프로세스: 추가로 당직자는 자연어로 시스템 정상인지 질의, 결과 확인후 보고

## Getting Started

1. 소스를 다운받습니다.
    ```bash
    git clone [REPO_URL]
    cd [REPO_NAME]
    ```

1. step01 경로로 이동합니다.
    ```bash
    REPOSITORY_ROOT=$(git rev-parse --show-toplevel)
    cd "$REPOSITORY_ROOT/step01"
    ```

1. config.ini를 생성합니다.
    ```bash
    cp config.sample.ini config.ini
    ```

1. 파이썬 가상환경을 설정합니다.
   ```bash
   # Mac
   uv venv .step01
   source .step01/bin/activate
   export UV_PROJECT_ENVIRONMENT=.step01 && uv sync
   ```

   ```bash
   # Windows
   uv venv .step01
    .\.step01\Scripts\Activate
   uv sync --active
   ```

1. 앱을 실행합니다.
    ```bash
    uv run --active uvicorn src.screenshotAgent:app --reload --port 9910
    ```

1. `/docs` Swagger 화면에 접속해 API 명세를 확인하세요.

1. Swagger 화면에서 `/mcp/screenshot` 엔드포인트에 요청내용을 입력하고 결과를 확인합니다.

    ```
    Q. https://news.jtbc.co.kr/ 사이트 접속해서 메인 기사 내용 요약좀 해줘
    A. 현재 JTBC 뉴스의 주요 기사 내용을 요약하면 다음과 같습니다: (이하 생략)
    ```

    ```
    Q. https://newstapa.org/ 사이트에 세금 오남용 추적 메뉴 접속해서 스크린샷 찍어줘.
    A. (캡처후 Base64로 인코딩한 이미지를 응답, 혹은 data/screenshot 경로에 파일로 저장)
    ```


## How to test

1. 테스트는 아래와 같이 실행합니다.
    ```bash
    # Mac/bash
    export UV_PROJECT_ENVIRONMENT=.step01 && uv sync --group test
    PYTHONPATH=$PWD/step01 pytest step01/tests
    ```

    ```bash
    # Windows/cmd
    set UV_PROJECT_ENVIRONMENT=.step01 && uv sync --group test
    PYTHONPATH=$PWD/step01 pytest step01/tests
    ```

    > 테스트 결과를 파일로 출력하려면 `PYTHONPATH=$PWD/step01 pytest step01/tests > pytest.log 2>&1` 또는 `PYTHONPATH=$PWD/step01 pytest step01/tests > pytest.log 2>&1` 명령어를 사용하세요.

## Code Convention

1. Python 코드가 Flake8 Convention을 준수하는지 다음과 같이 확인합니다.
    ```bash
    # Mac/bash
    export UV_PROJECT_ENVIRONMENT=.step01 && uv sync --group dev
    flake8 src/ tests/ --count --show-source --statistics
    ```

    ```bash
    # Windows/cmd
    set UV_PROJECT_ENVIRONMENT=.step01 && uv sync --group dev
    flake8 src/ tests/ --count --show-source --statistics
    ```

    > 검증 결과를 파일로 출력하려면 `flake8 src/ tests/ --count --show-source --statistics > flake8.log 2>&1` 명령어를 사용하세요.

2. API 설계가 Convention을 준수하는지 openapi-spec-validator를 사용해 다음과 같이 확인합니다.
    ```bash
    # Mac/bash
    export UV_PROJECT_ENVIRONMENT=.step01 && uv sync --group dev
    uv run --active uvicorn src.screenshotAgent:app --reload --port 9910 &
    curl http://localhost:9910/openapi.json -o openapi.json
    pkill -f uvicorn
    openapi-spec-validator openapi.json
    ```

    ```cmd
    # Windows/cmd
    set UV_PROJECT_ENVIRONMENT=.step01
    uv sync --group dev
    start "uvicorn" uv run --active uvicorn src.screenshotAgent:app --reload --port 9910
    timeout /t 3 >nul
    curl http://localhost:9910/openapi.json -o openapi.json
    taskkill /IM uvicorn.exe /F
    openapi-spec-validator openapi.json
    ```

    > 검증 결과를 파일로 출력하려면 `openapi-spec-validator openapi.json > openapi-validation.log 2>&1` 명령어를 사용하세요.

