
class Timing:
    def __init__(self, stats={}, configuration={}, grid={}, extra={}):
        self.stats = stats
        self.configuration = configuration
        self.grid = grid
        self.extra = extra

    def set_grid(self, grid):
        self.grid = grid
        return self
    
    def get_grid(self):
        return self.grid

    def set_configuration(self, configuration):
        self.configuration = configuration
        return self
    
    def get_configuration(self):
        return self.configuration

    def set_stats(self, stats):
        self.stats = stats
        return self
    
    def get_stats(self):
        return self.stats

    def set_extra(self, extra):
        self.extra = extra
        return self

    def get_extra(self):
        return self.extra

    def from_dict(self, dict):
        self.stats = dict['stats'] if 'stats' in dict else {}
        self.configuration = dict['configuration'] if 'configuration' in dict else {}
        self.grid = dict['grid'] if 'grid' in dict else {}
        self.extra = dict['extra'] if 'extra' in dict else {}
        return self

    def to_object(self):
        return {
            'configuration': self.configuration,
            'stats': self.stats,
            'grid': self.grid,
            'extra': self.extra
        }
