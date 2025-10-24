# README

This project is a toolkit for collecting web documents and screenshots for static analysis.  
It is Windows-dependent, primarily uses a locally served Ollama model,  
and is designed to fall back to Azure AI Foundry if needed.

## Getting Started

1. Get the code

    ```bash
    git clone {REPO_URL}
    cd {REPO_NAME}
    ```

1. Make sure you're at the project root.

    ```bash
    REPO_ROOT=$(git rev-parse --show-toplevel)
    cd "$REPO_ROOT"
    ```

1. Activate uv environment.

    ```bash
    uv venv .venv

    # Windows
    .venv\Scripts\activate
    ```

    > **NOTE**: This project is dependent on Windows and currently does not support Linux or Mac.

1. Run the code

    ```bash
    uv run -m src.main
    ```