import os
import signal

from lib.Crawler import Crawler

EVENT_NAME = 'Resistencia%20Los%20Santos%2018-07-2020'
API_TOKEN = 'd265aed699f7409ac0ec6fe07ee9cb11'

MESSAGES_PATH = '../../artifacts/logs/se_combined'
USE_WEBSOCKET_LISTENER = False # True: use websocket; False: use files in MESSAGES_PATH

STOP_IF_ERROR = False
ERRORS_PATH = '../../artifacts/logs/errors'

crawler = None

def create_dir(base_path: str, path: str):
    path = base_path + '/' + path
    if not os.path.exists(path):
        os.makedirs(path)

def close(_signo, _stack_frame):
    global crawler
    exit(0)

if __name__ == '__main__':
    # Signals
    signal.signal(signal.SIGINT, close)
    signal.signal(signal.SIGTERM, close)
    
    base_path = os.path.dirname(os.path.realpath(__file__))
    create_dir(base_path, ERRORS_PATH)

    crawler = Crawler(EVENT_NAME, API_TOKEN, base_path, MESSAGES_PATH, ERRORS_PATH,
                      USE_WEBSOCKET_LISTENER, STOP_IF_ERROR, reset_last=True)
    crawler.run()
