import glob

from .MessagesParser import MessagesParser

class WebSocketParser:
    def __init__(self, parser: MessagesParser, file_path: str):
        self.parser = parser
        self.file_path = '%s/*.txt' % file_path

        # Init list and iterator
        self.i = 0
        self.file_list = [f for f in glob.glob(self.file_path)]
        self.file_list = sorted(self.file_list)

    def run(self):
        if self.i >= len(self.file_list):
            print('#' * 10)
            print('CLOSE SIM-CONNECTION')
            return None

        with open(self.file_list[self.i], 'r') as fp:
            self.i = self.i + 1
            print('File %d of %d' % (self.i, len(self.file_list)))
            message = fp.read()
            print('Parsing message...')
            return self.parser.parse_message(message)
