"""
Automated Screenshot Agent: Main entrypoint
- 파이프라인 직접 실행용
- 추후 REST/Socket 서버로 확장 가능
"""

from src.scheduler import main as scheduler_main

if __name__ == "__main__":
    scheduler_main()