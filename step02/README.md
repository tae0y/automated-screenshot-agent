# STEP 02 : 멀티 Agent Workflow를 통해 테스트결과를 검증

- 당초 프로세스: 추가로 당직자는 자연어로 시스템 정상인지 질의, 결과 확인후 보고
- 변경 프로세스: Worker는 시스템 점검 수행, Manager는 점검 결과를 검토하고 불충분하면 재시도

## Getting Started

1. 소스를 다운받습니다.
    ```bash
    git clone [REPO_URL]
    cd [REPO_NAME]
    ```

1. step02 경로로 이동합니다.
    ```bash
    REPOSITORY_ROOT=$(git rev-parse --show-toplevel)
    cd "$REPOSITORY_ROOT/step02"
    ```

1. config.ini를 생성합니다.
    ```bash
    cp config.sample.ini config.ini
    ```

1. 파이썬 가상환경을 설정합니다.
    ```bash
    # Mac
    uv venv .step02
    source .step02/bin/activate
    export UV_PROJECT_ENVIRONMENT=.step02 && uv sync
    uv run playwright install
    ```

    ```bash
    # Windows
    uv venv .step02
    .\.step02\Scripts\Activate
    uv sync --active --prerelease allow
    uv run playwright install
    ```

1. 앱을 실행합니다.
    ```bash
    uv run --active uvicorn src.screenshotAgent:app --port 9910
    ```
    > In Windows, turn off `--reload` option to use playwright.

1. `/docs` Swagger 화면에 접속해 API 명세를 확인하세요.

1. 위와 같이 앱을 실행한 다음 외부 스케줄러를 사용해 호출합니다.

## How to test

1. 테스트는 아래와 같이 실행합니다.
    ```bash
    # Mac/bash
    export UV_PROJECT_ENVIRONMENT=.step02 && uv sync --group test
    PYTHONPATH=$PWD/step02 pytest step02/tests
    ```

    ```bash
    # Windows/cmd
    set UV_PROJECT_ENVIRONMENT=.step02 && uv sync --group test
    PYTHONPATH=$PWD/step02 pytest step02/tests
    ```

    > 테스트 결과를 파일로 출력하려면 `PYTHONPATH=$PWD/step02 pytest step02/tests > pytest.log 2>&1` 또는 `PYTHONPATH=$PWD/step02 pytest step02/tests > pytest.log 2>&1` 명령어를 사용하세요.

## Code Convention

1. Python 코드가 Flake8 Convention을 준수하는지 다음과 같이 확인합니다.
    ```bash
    # Mac/bash
    export UV_PROJECT_ENVIRONMENT=.step02 && uv sync --group dev
    flake8 src/ tests/ --count --show-source --statistics
    ```

    ```bash
    # Windows/cmd
    set UV_PROJECT_ENVIRONMENT=.step02 && uv sync --group dev
    flake8 src/ tests/ --count --show-source --statistics
    ```

    > 검증 결과를 파일로 출력하려면 `flake8 src/ tests/ --count --show-source --statistics > flake8.log 2>&1` 명령어를 사용하세요.

2. API 설계가 Convention을 준수하는지 openapi-spec-validator를 사용해 다음과 같이 확인합니다.
    ```bash
    # Mac/bash
    export UV_PROJECT_ENVIRONMENT=.step02 && uv sync --group dev
    uv run --active uvicorn src.screenshotAgent:app --reload --port 9910 &
    curl http://localhost:9910/openapi.json -o openapi.json
    pkill -f uvicorn
    openapi-spec-validator openapi.json
    ```

    ```cmd
    # Windows/cmd
    set UV_PROJECT_ENVIRONMENT=.step02
    uv sync --group dev
    start "uvicorn" uv run --active uvicorn src.screenshotAgent:app --reload --port 9910
    timeout /t 3 >nul
    curl http://localhost:9910/openapi.json -o openapi.json
    taskkill /IM uvicorn.exe /F
    openapi-spec-validator openapi.json
    ```

    > 검증 결과를 파일로 출력하려면 `openapi-spec-validator openapi.json > openapi-validation.log 2>&1` 명령어를 사용하세요.

