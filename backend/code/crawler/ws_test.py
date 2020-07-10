import websocket
import os
import time
from datetime import datetime
import random

try:
    import thread
except ImportError:
    import _thread as thread

LOGS_PATH = '../../artifacts/logs'

current_time = lambda: datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')

# Create logs folder
current_path = os.path.dirname(os.path.realpath(__file__))
abs_logs_path = current_path + '/' + LOGS_PATH
if not os.path.exists(abs_logs_path):
    os.makedirs(abs_logs_path)

def on_message(ws, message):
    print('#' * 20, 'MESSAGE', '#' * 20)
    print(message)
    print('')
    abs_logs_file = abs_logs_path + '/' + '%d_rd%d.txt' % (current_time(), random.randint(0, 100))
    f = open(abs_logs_file, "a")
    f.write(message)
    f.close()

def on_error(ws, error):
    print('#' * 20, 'ERROR', '#' * 20)
    print(error)

def on_close(ws):
    print('#' * 20, 'CLOSED', '#' * 20)

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send('Hello %d' % i)
        time.sleep(1)
        ws.close()
        print('thread terminating...')
    thread.start_new_thread(run, ())


if __name__ == '__main__':
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('ws://www.apex-timing.com:8092',
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
