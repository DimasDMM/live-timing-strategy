from .ParserInterface import ParserInterface
import re

class StageParser(ParserInterface):
    def __init__(self):
        # Map columns
        self.map_titles = {
            'Clasificación': 'position',
            'Kart': 'team_number',
            'Equipo': 'team_name',
            'Última vuelta': 'time',
            'Gap': 'gap',
            'Vueltas': 'lap',
            'Pits': 'number_stops',
            'En Pista': 'driving_time'
        }

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
