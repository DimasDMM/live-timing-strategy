from .BaseParser import BaseParser
import re

class StageParser(BaseParser):
    def parse(self, data, timing):
        title = data[2]

        if title == 'Clasificación':
            stage = 'classification'
        elif re.search('^Carrera', title):
            stage = 'race'
        else:
            stage = 'unknown'

        stats = timing.get_stats()
        stats['stage'] = stage
        timing.set_stats(stats)

        return timing
