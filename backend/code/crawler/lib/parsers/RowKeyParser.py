from .BaseParser import BaseParser

import re

class RowKeyParser(BaseParser):
    def parse(self, data, timing):
        if data[1] in ['*', '*out', '*in']:
            # Nothing to do
            pass
        elif data[1] == '#':
            # Position
            if data[2].isnumeric():
                grid = timing.get_grid()
                position = int(data[2])
                grid[data[0]]['position'] = position
                if position == 1:
                    grid[data[0]]['interval'] = 0
        else:
            raise Exception('UNKNOWN ROW UPDATE')
        return timing
