import sys

from src.config import ConfigManager
from src.logger import get_logger


def capture():
    """
    스크린샷 캡처 진입점
    """
    # Playwright를 사용해 캡처한다
    # network idle 상태가 될 때까지 대기한다
    # idle이 발생하지 않더라도 TIMEOUT 이후에는 강제 캡처한다
    # 캡처한 이미지를 WEBP_QUALITY, IMG_MAX_WIDTH에 맞게 변환한다
    _logger.info("here comes the capture...")
    pass


def main():
    """
    http.server 진입점
    """
    # 9910 포트로 요청을 수신하는 http.server
    # 요청에서 파라미터를 읽어 비즈니스 로직을 실행한다
    # config에 따라 병렬로 실행할 건수를 정하고
    # config에 정의된 URL 목록을 캡처해 지정된 경로에 저장한다

    pass


def test():
    """
    테스트 진입점
    """
    # 테스트 파라미터를 사용해 비즈니스 로직을 실행한다
    # config에 따라 병렬로 실행할 건수를 정하고
    # config에 정의된 URL 목록을 캡처해 지정된 경로에 저장한다
    _logger.info("here comes the test...")
    capture()
    pass


if __name__ == "__main__":
    global _config, _logger
    _config = ConfigManager()
    _logger = get_logger(__name__)
    _logger.info("""

███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗███████╗██╗  ██╗ ██████╗ ████████╗
██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║██╔════╝██║  ██║██╔═══██╗╚══██╔══╝
███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║███████╗███████║██║   ██║   ██║
╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║╚════██║██╔══██║██║   ██║   ██║
███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║███████║██║  ██║╚██████╔╝   ██║
╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝

 █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝

Now starting the Automated Screenshot Agent...
""")

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test()
    else:
        main()
