import json
import os
import random
import time
from datetime import datetime
import websocket

from .MessagesParser import MessagesParser

class WebSocketListener:
    def __init__(self, url: str, parser: MessagesParser, save_messages=None):
        self.url = url
        self.parser = parser
        self.save_messages = save_messages

        # Last timing object
        self.timing = None

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
        self.timing = self.parser.parse_message(message)

    def on_error(self, ws, error):
        self.parser.parse_error(error)

    def on_open(self, ws):
        pass

    def on_close(self, ws):
        pass

    def _current_time(self):
        return datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')
