from .ParserInterface import ParserInterface
from .ApiRequests import ApiRequests

from .parsers.GridParser import GridParser
from .parsers.StageParser import StageParser
from .Timing import Timing

from io import StringIO
import pandas as pd
import json
import os

class WebSocketParser:
    def __init__(self, timing: Timing, api: ApiRequests, debug=False):
        self.timing = timing
        self.api = api
        self.debug = debug

        # Parsers
        self.parsers = {
            'grid': GridParser(),
            'title2': StageParser()
        }

    def parse_message(self, message: str):
        io_message = StringIO(message)
        df = pd.read_csv(io_message, sep='|', header=None)

        for _, row in df.iterrows():
            parser_found = False
            if row[0] in self.parsers:
                self.timing = self.parsers[row[0]].parse(row, self.timing)
                parser_found = True
            
            if not parser_found:
                # No parser for this message
                print(message)
                raise Exception('NO PARSER')

    def parse_error(self, error: str):
        pass

    def set_timing(self, timing: Timing):
        self.timing = timing

    def get_timing(self):
        return self.timing
