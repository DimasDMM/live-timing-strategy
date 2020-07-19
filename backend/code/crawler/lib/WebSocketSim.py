import glob

from .ParserInterface import ParserInterface

class WebSocketSim:
    def __init__(self, url: str, parser: ParserInterface, sim_file_path: str):
        self.url = url
        self.parser = parser
        self.sim_file_path = sim_file_path

        # Init list and iterator
        self.i = 0
        self.file_list = [f for f in glob.glob(self.sim_file_path)]

    def run(self):
        if self.i > len(self.file_list):
            return None

        with open(self.file_list[self.i], 'r') as fp:
            self.i = self.i + 1
            message = fp.read()
            return self.parser.parse_message(message)
