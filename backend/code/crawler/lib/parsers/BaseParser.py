from .ParserInterface import ParserInterface

import re

class BaseParser(ParserInterface):
    def __init__(self):
        # Columns with a time to be transformed into integer
        self.cast_columns = {
            'position': self._cast_int,
            'team_number': self._cast_int,
            'lap': self._cast_int,
            'number_stops': self._cast_int,
            'time': self._cast_time_to_int,
            'best_time': self._cast_time_to_int,
            'driving_time': self._cast_time_to_int
        }

    def parse(self, data, timing):
        return timing

    def _cast_time_to_int(self, val, stats):
        if re.search(r'^(?:(\d+):)?(\d+)\.(\d*)$', val):
            time_parts = re.findall(r'^(?:(\d+):)?(\d+)\.(\d*)$', val)[0]
            minutes, seconds, milliseconds = time_parts
            minutes = minutes if minutes != '' else 0
            seconds = seconds if seconds != '' else 0
            milliseconds = milliseconds if milliseconds != '' else 0
            int_time = int(minutes) * 60000 + int(seconds) * 1000 + int(milliseconds)
        elif re.search(r'^(\d+):(\d+)$', val):
            time_parts = re.findall(r'^(\d+):(\d+)$', val)[0]
            int_time = int(time_parts[0]) * 60 * 60 * 1000 + int(time_parts[1]) * 60 * 1000
        else:
            int_time = None
        return int_time
    
    def _cast_int(self, val, stats):
        return 0 if val == '' else int(val)

    def _clean_html(self, raw_html):
        cleanr = re.compile('<.*?>')
        return re.sub(cleanr, '', raw_html)
