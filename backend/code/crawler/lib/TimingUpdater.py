import json
import os
import random
import time
from datetime import datetime

import websocket

from .ParserInterface import ParserInterface

try:
    import thread
except ImportError:
    import _thread as thread

class TimingUpdater:
    def __init__(self, api, event_name, event_config, initial_timing=[]):
        self.api = api
        self.event_name = event_name
        self.event_config = event_config
        self.timing = initial_timing

    def update_timing(self, timing, stats):
        if len(self.timing) == 0 or self.timing is None:
            self._init_teams(timing, stats)
        
        last_times = self._get_last_times(timing, stats)

    def _init_teams(self, timing, stats):
        # Add teams
        path = '/v1/events/%s/teams' % (self.event_name)
        for row in timing:
            team = {
                'name': row['team_name'],
                'number': row['team_number'],
                'drivers': [],
                'reference_time_offset': 0
            }
            self.api.post(path, team)

    def _get_last_times(self, timing):
        last_times = []
        for row in timing:
            pass
            
        return last_times

    def _current_time(self):
        return datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')
