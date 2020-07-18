import json
import os
import random
import time
from datetime import datetime

import websocket

from .ParserInterface import ParserInterface

try:
    import thread
except ImportError:
    import _thread as thread

class WebSocket:
    def __init__(self, url: str, parser: ParserInterface, save_messages=None, ws=None):
        self.url = url
        self.parser = parser
        self.save_messages = save_messages
        self._load_settings()

        # Build web socket
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)

    def run(self):
        self.ws.run_forever()
        return self.parser.get_current_timing()

    def on_message(self, ws, message):
        if self.save_messages is not None:
            current_path = os.path.dirname(os.path.realpath(__file__))
            filename = '%s_rd%d.txt' % (self._current_time(), random.randint(0, 100))
            file_path = current_path + '/' + self.save_messages + '/' + filename
            f = open(file_path, 'w')
            f.write(message)
            f.close()
        self.parser.on_message(message)

    def on_error(self, ws, error):
        self.parser.on_error(error)

    def on_close(self, ws):
        pass

    def on_open(self, ws):
        def run(*args):
            for i in range(3):
                time.sleep(1)
                ws.send('Hello %d' % i)
            time.sleep(1)
            ws.close()
            print('thread terminating...')
        thread.start_new_thread(run, ())

    def _load_settings(self):
        if self.file_settings is not None:
            try:
                with open(self.file_settings, 'r') as fp:
                    self.settings = json.load(fp)
            except Exception as e:
                print('Error: %s' % str(e))
                raise e

    def _current_time(self):
        return datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')
