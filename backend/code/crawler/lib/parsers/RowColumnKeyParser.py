from .BaseParser import BaseParser

import math
import re

class RowColumnKeyParser(BaseParser):
    def parse(self, data, timing):
        matches = re.findall(r'^(.+?)c(\d+)$', data[0])[0]
        team_key = matches[0]
        
        extra = timing.get_extra()
        column_name = extra['grid_columns'][int(matches[1]) - 1]
        
        grid = timing.get_grid()
        stats = timing.get_stats()
        
        if column_name == 'team_name':
            # Update of team name or driver name
            team_driver_name = data[2].strip()
            
            if data[1] == 'dr':
                # Team name
                grid[team_key]['team_name'] = team_driver_name
            elif data[1] == 'drteam':
                # Driver name
                team_driver_name = re.findall(r'^(.*?)(?:\[(\d:\d+)\])?$', team_driver_name)[0]
                
                driver_name = team_driver_name[0].strip()
                
                if 'drivers' not in grid[team_key]:
                    grid[team_key]['drivers'] = {}
                
                # Set as non-active to all drivers in the team
                for name in grid[team_key]['drivers']:
                    grid[team_key]['drivers'][name]['active'] = False
                
                if driver_name not in grid[team_key]['drivers']:
                    grid[team_key]['drivers'][driver_name] = {
                        'driving_time': 0,
                        'reference_time_offset': 0,
                        'active': True
                    }
                
                if data[1] == 'in':
                    driving_time = self._cast_time_to_int(team_driver_name[1], stats)
                    grid[team_key]['drivers'][driver_name]['driving_time'] = driving_time
                    grid[team_key]['drivers'][driver_name]['active'] = True
                    grid[team_key]['in_box'] = False
                elif data[1] == 'to':
                    # Driver in box
                    grid[team_key]['in_box'] = True
            else:
                raise Exception('UNKNOWN TEAM-ROW UPDATE')
        elif column_name == 'interval':
            if (isinstance(data[2], int) or isinstance(data[2], float)) and math.isnan(data[2]):
                # Nothing to parse
                return timing
            
            if grid[team_key]['position'] == 1:
                grid[team_key]['interval'] = 0
                grid[team_key]['interval_unit'] = 'milli'
            else:
                column_value = data[2].strip()
                
                if re.search(r'^\d+ vueltas?$', column_value):
                    interval_parts = re.findall(r'^(\d+) vueltas?$', column_value)[0]
                    grid[team_key]['interval'] = self._cast_int(interval_parts, stats)
                    grid[team_key]['interval_unit'] = 'laps'
                else:
                    grid[team_key]['interval'] = self._cast_time_to_int(column_value, stats)
                    grid[team_key]['interval_unit'] = 'milli'
        elif column_name != '':
            # Update of any other column value
            column_value = data[2].strip()
            if column_name in self.cast_columns:
                column_value = self.cast_columns[column_name](column_value, stats)

            grid[team_key][column_name] = column_value
            
            if column_name == 'position' and column_value == 1:
                grid[team_key]['interval'] = 0
                grid[team_key]['interval_unit'] = 'milli'
        
        return timing
