# README

This project is a toolkit for collecting web documents and screenshots for static analysis.  
It is Windows-dependent, primarily uses a locally served Ollama model,  
and is designed to fall back to Azure AI Foundry if needed.

## Getting Started

1. Get the code.

    ```bash
    git clone {REPO_URL}
    cd {REPO_NAME}
    ```

1. Make sure you're at the project root.

    ```bash
    REPO_ROOT=$(git rev-parse --show-toplevel)
    cd "$REPO_ROOT"
    ```

1. Run the docker db, dbadmin containers.

    ```bash
    cd "$REPO_ROOT"/docker
    docker-compose up -d
    ```

1. Activate uv python environment.

    ```bash
    cd "$REPO_ROOT"

    uv venv .venv && uv sync
    playwright install

1. (선택) 저장 경로 등 환경설정

    프로젝트 루트에 .env 파일을 생성해 아래와 같이 저장 경로를 지정할 수 있습니다:

    ```env
    OUTDIR=data
    ```

    기본값은 data 폴더이며, 원하는 경로로 변경 가능합니다.

    # Windows
    .venv\Scripts\activate
    ```

    > **NOTE**: This project is dependent on Windows and currently does not support Linux or Mac.

1. Run the app.

    ```bash
    uv run -m src.main
    ```