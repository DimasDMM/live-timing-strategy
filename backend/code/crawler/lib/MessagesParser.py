from .ApiRequests import ApiRequests

from .parsers.Dyn1Parser import Dyn1Parser
from .parsers.GridParser import GridParser
from .parsers.NoneParser import NoneParser
from .parsers.StageParser import StageParser
from .parsers.RowColumnKeyParser import RowColumnKeyParser
from .parsers.RowKeyParser import RowKeyParser
from .Timing import Timing

from io import StringIO
import pandas as pd
import json
import os
import re

class MessagesParser:
    def __init__(self, timing: Timing, api: ApiRequests):
        self.timing = timing
        self.api = api

        self.MAX_NUMBER_COLUMNS = 20

        # Parsers
        none_parser = NoneParser()
        self.parsers = {
            'init': none_parser,
            'best': none_parser,
            'css': none_parser,
            'grid': GridParser(),
            'effects': none_parser,
            'comments': none_parser,
            'title1': none_parser,
            'title2': StageParser(),
            'dyn1': Dyn1Parser(),
            'light': none_parser,
            'wth1': none_parser,
            'wth2': none_parser,
            'wth3': none_parser,
            'track': none_parser,
            'com': none_parser,
            'msg': none_parser,
            'row_column_key_parser': RowColumnKeyParser(),
            'row_key_parser': RowKeyParser()
        }

    def parse_message(self, message: str):
        try:
            message_rows = message.split('\n')            
            team_keys = list(self.timing.get_grid().keys())

            for message_row in message_rows:
                if message_row.strip() == '':
                    continue

                # Parse each row independently since they may contain a different number of columns
                io_message = StringIO(message_row)
                row = pd.read_csv(io_message, sep='|', header=None, dtype=str).iloc[0]
                
                if row[0] in self.parsers:
                    self.timing = self.parsers[row[0]].parse(row, self.timing)
                elif re.search(r'^.+?c\d+$', row[0]):
                    self.parsers['row_column_key_parser'].parse(row, self.timing)
                elif row[0] in team_keys:
                    self.parsers['row_key_parser'].parse(row, self.timing)
                else:
                    # No parser for this message
                    raise Exception('NO PARSER')
        except Exception as e:
            raise Exception({message, e})
            
        return self.timing

    def parse_error(self, error: str):
        pass

    def set_timing(self, timing: Timing):
        self.timing = timing

    def get_timing(self):
        return self.timing
