from .ParserInterface import ParserInterface
import re

class GridParser(ParserInterface):
    def __init__(self):
        # Map columns
        self.map_columns = {
            'Clasif.': 'position',
            'Kart': 'team_number',
            'Equipo': 'team_name',
            'Última vuelta': 'time',
            'Interv.': 'gap',
            'Vueltas': 'lap',
            'Pits': 'number_stops',
            'En Pista': 'driving_time'
        }

        # Columns with a time to be transformed into integer
        self.cast_columns = {
            'position': self._cast_int,
            'team_number': self._cast_int,
            'lap': self._cast_int,
            'number_stops': self._cast_int,
            'time': self._cast_time_to_int,
            'gap': self._cast_time_to_int,
            'driving_time': self._cast_time_to_int
        }

    def parse(self, data, timing):
        raw_grid = {}
        grid_html = data[2]

        # Extract HTML data
        html_rows = re.search('<tbody>(.+?)</tbody>', grid_html)
        html_rows = re.findall('<tr.*? data-id="(.+?)".*?>(.+?)</tr>', html_rows[0])

        # Get column names
        header_row = html_rows[0][1]
        column_names = re.findall('<td.*?>(.*?)</td>', header_row)
        
        # Parse each grid row
        timing_rows = html_rows[1:]
        for html_row in timing_rows:
            column_values = re.findall('<td(:?.+?)>(.*?)</td>', html_row[1])

            i = 0
            parsed_row = {}
            for column_value in column_values:
                parsed_row[column_names[i]] = self._clean_html(column_value[1])
                i = i + 1
            
            raw_grid[html_row[0]] = parsed_row

        # Map columns
        parsed_grid = {}
        parsed_column_names = []
        for row_id, raw_row in raw_grid.items():
            row = {x:None for x in self.map_columns.values()}
            for col_key, col_val in raw_row.items():
                if col_key not in self.map_columns:
                    parsed_column_names.append('')
                    continue
                else:
                    parsed_column_names.append(self.map_columns[col_key])
                
                mapped_key = self.map_columns[col_key]

                # Transform time if needed
                if mapped_key in self.cast_columns:
                    col_val = self.cast_columns[mapped_key](col_val, timing.get_stats())

                row[mapped_key] = col_val
            parsed_grid[row_id] = row

        timing.set_grid(parsed_grid)
        
        # Save column names
        extra = timing.get_extra()
        if 'grid_columns' not in extra:
            extra['grid_columns'] = parsed_column_names
            timing.set_extra(extra)

        return timing

    def _cast_time_to_int(self, val, stats):
        if re.search(r'^(?:(\d+):)?(\d+)\.(\d{3})$', val):
            time_parts = re.findall(r'^(?:(\d+):)?(\d+)\.(\d{3})$', val)[0]
            minutes, seconds, milliseconds = time_parts
            minutes = minutes if minutes != '' else 0
            int_time = int(minutes) * 60000 + int(seconds) * 1000 + int(milliseconds)
        elif re.search(r'^(\d+):(\d+)$', val):
            time_parts = re.findall(r'^(\d+):(\d+)$', val)[0]
            int_time = int(time_parts[0]) * 60000 + int(time_parts[1]) * 1000
        elif re.search(r'^(\d+) vueltas?$', val):
            time_parts = re.findall(r'^(\d+) vueltas?$', val)[0]
            int_time = time_parts[0] * (int(stats['reference_time']) + int(stats['reference_current_offset']))
        else:
            int_time = None
        return int_time
    
    def _cast_int(self, val, stats):
        return 0 if val == '' else int(val)

    def _clean_html(self, raw_html):
        cleanr = re.compile('<.*?>')
        return re.sub(cleanr, '', raw_html)
