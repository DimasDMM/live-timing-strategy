from .BaseParser import BaseParser

import copy
import re

class GridParser(BaseParser):
    def __init__(self):
        # Map columns
        self.map_columns = {
            'Clasif.': 'position',
            'Kart': 'team_number',
            'Equipo': 'team_name',
            'Última vuelta': 'time',
            'Mejor vuelta': 'best_time',
            'Interv.': 'interval',
            'Vueltas': 'lap',
            'Pits': 'number_stops',
            'En Pista': 'driving_time'
        }
        self.default_grid_row = {
            'position': None,
            'team_number': None,
            'team_name': None,
            'time': None,
            'best_time': None,
            'interval': None,
            'interval_unit': None,
            'lap': None,
            'number_stops': None,
            'driving_time': None,
            'in_box': False,
            'drivers': {}
        }
        
        super().__init__()

    def parse(self, data, timing):
        grid_html = data[2]

        # Extract HTML data
        html_rows = re.search(r'<tbody>(.+?)</tbody>', grid_html)
        html_rows = re.findall(r'<tr.*? data-id="(.+?)".*?>(.+?)</tr>', html_rows[0])

        # Get column names
        header_row = html_rows[0][1]
        raw_column_names = re.findall(r'<td.*?>(.*?)</td>', header_row)
        
        column_names = []
        for raw_column_name in raw_column_names:
            if raw_column_name.strip() not in self.map_columns:
                column_names.append('')
            else:
                column_name = self.map_columns[raw_column_name.strip()]
                column_names.append(column_name)
        
        # Parse each grid row
        timing_rows = html_rows[1:]
        grid = timing.get_grid()
        for html_row in timing_rows:
            columns_data = re.findall(r'<td.*?(?:class="(.*?)")?>(.*?)</td>', html_row[1])
            team_key = html_row[0]
            
            # Init row if needed
            if team_key not in grid:
                grid[team_key] = copy.deepcopy(self.default_grid_row)
            
            for i, column_data in enumerate(columns_data):
                raw_column_name = raw_column_names[i].strip()
                
                column_class = column_data[0].strip()
                
                column_value = column_data[1].strip()
                column_value = self._clean_html(column_value)

                # Ignore column or map it
                if raw_column_name not in self.map_columns:
                    continue
                else:
                    column_name = self.map_columns[raw_column_name]
                
                if column_name == 'team_name' and column_class == 'drteam':
                    # Driver name, not team name
                    driver_data = re.findall(r'^(.*?)(?:\[(\d:\d+)\])?$', column_value)[0]
                    driver_name = driver_data[0].strip()
                    
                    for driver_name in grid[team_key]['drivers']:
                        grid[team_key]['drivers'][driver_name]['active'] = False

                    # Set as active driver
                    if driver_name not in grid[team_key]['drivers']:
                        grid[team_key]['drivers'][driver_name] = {
                            'active': True,
                            'driving_time': 0 if ('driving_time' not in grid[team_key] or grid[team_key]['driving_time'] is None) else grid[team_key]['driving_time'],
                            'reference_time_offset': 0
                        }
                    else:
                        grid[team_key]['drivers'][driver_name]['active'] = True
                elif column_name == 'driving_time':
                    if column_class == 'to':
                        # Driver in box
                        grid[team_key]['in_box'] = True
                    else:
                        # Set driving time to active driver too
                        driving_time = self.cast_columns[column_name](column_value, timing.get_stats())
                        driving_time = 0 if driving_time is None else driving_time
                        
                        grid[team_key]['in_box'] = False
                        
                        grid[team_key]['driving_time'] = driving_time
                        for driver_name in grid[team_key]['drivers']:
                            if grid[team_key]['drivers'][driver_name]['active']:
                                grid[team_key]['drivers'][driver_name]['driving_time'] = driving_time
                elif column_name == 'interval':
                    if re.search(r'^\d+ [Vv]ueltas?$', column_value):
                        interval_parts = re.findall(r'^(\d+) [Vv]ueltas?$', column_value)[0]
                        grid[team_key]['interval'] = self._cast_int(interval_parts, timing.get_stats())
                        grid[team_key]['interval_unit'] = 'laps'
                    else:
                        interval = self._cast_time_to_int(column_value, timing.get_stats())
                        grid[team_key]['interval'] = 0 if interval is None else interval
                        grid[team_key]['interval_unit'] = 'milli'
                else:
                    # Transform value if needed
                    if column_name in self.cast_columns:
                        column_value = self.cast_columns[column_name](column_value, timing.get_stats())

                    grid[team_key][column_name] = column_value
                    
                    if column_name == 'position' and column_value == 1:
                        grid[team_key]['interval'] = 0
                        grid[team_key]['interval_unit'] = 'milli'
                    elif column_name == 'driving_time' and column_value is not None:
                        for driver_name in grid[team_key]['drivers']:
                            if grid[team_key]['drivers'][driver_name]['active']:
                                grid[team_key]['drivers'][driver_name]['driving_time'] = column_value

        timing.set_grid(grid)
        
        # Save column names
        extra = timing.get_extra()
        if 'grid_columns' not in extra:
            extra['grid_columns'] = column_names
            timing.set_extra(extra)

        return timing
