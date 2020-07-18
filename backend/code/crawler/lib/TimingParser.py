from .ParserInterface import ParserInterface
from .ApiRequests import ApiRequests
import json
import re
import os

class TimingParser(ParserInterface):
    def __init__(self, timing: list, api: ApiRequests, debug=False):
        self.timing = timing
        self.api = api
        self.debug = debug

        self.timing = {}

        # Map columns
        self.map_columns = {
            'Clasif.': 'position',
            'Kart': 'team_number',
            'Última vuelta': 'time',
            'Gap': 'gap',
            'Vueltas': 'lap',
            'Pits': 'number_stops',
            '-': 'team_name',
            '--': 'driver_name'
        }

    def on_message(self, message: str):
        # Full HTML in message
        if re.search('grid\|\|(.+?)\n', message, re.MULTILINE):
            result = re.search('grid\|\|(.+?)\n', message, re.MULTILINE)
            data = self._parse_rows(result[1])
            self.timing = data

    def on_error(self, error: str):
        pass

    def set_timing(self, timing):
        self.timing = timing

    def get_timing(self):
        return self.timing

    def _parse_rows(self, grid_html):
        raw_rows = []

        # Extract HTML column values
        html_rows = re.search('<tbody>(.+?)</tbody>', grid_html)
        html_rows = re.findall('<tr.*?>(.+?)</tr>', html_rows[0])

        header_row = html_rows[0]
        column_names = re.findall('<td.*?>(.*?)</td>', header_row)

        timing_rows = html_rows[1:]
        for html_row in timing_rows:
            column_values = re.findall('<td(:?.+?)>(.*?)</td>', html_row)

            i = 0
            parsed_row = {}
            for column_value in column_values:
                parsed_row[column_names[i]] = self._clean_html(column_value[1])
                i = i + 1
            
            raw_rows.append(parsed_row)

        # Map columns
        parsed_rows = []
        for raw_row in raw_rows:
            row = {x:None for x in self.map_columns.values()}
            for col_key, col_val in raw_row.items():
                if col_key not in self.map_columns:
                    continue
                row[self.map_columns[col_key]] = col_val
            parsed_rows.append(row)

        return parsed_rows

    def _clean_html(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
