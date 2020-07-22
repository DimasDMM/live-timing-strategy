from .BaseParser import BaseParser
import re

class Dyn1Parser(BaseParser):
    def parse(self, data, timing):
        dyn_type = data[1]

        if dyn_type == 'countdown':
            stats = timing.get_stats()
            stats['remaining_event'] = int(data[2])
            stats['remaining_event_unit'] = 'milli'
            timing.set_stats(stats)
        elif dyn_type in ['text']:
            # Do nothing
            pass
        else:
            raise Exception('UNKNOWN DYN1')

        return timing
