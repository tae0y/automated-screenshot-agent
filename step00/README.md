# STEP 00 : 매일아침 자동으로 스크린샷

- 당초 프로세스: 시스템에 접속해 점검후 보고(20분 내외)
- 변경 프로세스: 스케줄 작업으로 스크린샷, 당직자는 확인후 보고(5분 내외)

## Getting Started

1. 소스를 다운받습니다.
    ```bash
    git clone [REPO_URL]
    cd [REPO_NAME]
    ```

1. step00 경로로 이동합니다.
    ```bash
    REPOSITORY_ROOT=$(git rev-parse --show-toplevel)
    cd "$REPOSITORY_ROOT/step00"
    ```

1. config.ini를 생성합니다.
    ```bash
    cp src/config.sample.ini src/config.ini
    ```

1. 파이썬 가상환경을 설정합니다.
   ```bash
   uv venv .step00
   source .step00/bin/activate
   export UV_PROJECT_ENVIRONMENT=.step00 && uv sync
   ```

1. 앱을 실행합니다.
    ```bash
    uv run --active uvicorn src.screenshotAgent:app --reload --port 9910
    ```

1. /docs Swagger 화면에 접속해 확인해봅시다.
