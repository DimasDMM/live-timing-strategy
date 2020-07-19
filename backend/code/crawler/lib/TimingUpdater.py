import json
import os
import copy
import time
from datetime import datetime

import websocket

from .ApiRequests import ApiRequests
from .Timing import Timing

class TimingUpdater:
    def __init__(self, api: ApiRequests, event_name: str, event_config: list, timing: Timing):
        self.api = api
        self.event_name = event_name
        self.event_config = event_config
        self.timing = copy.deepcopy(timing)

    def update_timing(self, new_timing: Timing):
        self._update_stats(new_timing)
        self._update_grid(new_timing)

    def _update_grid(self, new_timing: Timing):
        # Api updates
        grid = self.timing.get_grid()
        for team_key, new_grid in new_timing.get_grid().items():
            if team_key not in grid:
                # New team, add it
                self._add_team(new_grid['team_name'], new_grid['team_number'])
            else:
                if grid[team_key]['team_name'] != new_grid[team_key]['team_name']:
                    # Update team name
                    self._update_team_name(grid[team_key]['team_name'], new_grid['team_name'])
                if grid[team_key]['team_number'] != new_grid[team_key]['team_number']:
                    # Update team number
                    self._update_team_number(new_grid['team_name'], new_grid['team_number'])
                if grid[team_key]['time'] != new_grid['time']:
                    # New time of the team
                    self._add_time(new_grid['team_name'], new_grid['time'], new_grid['gap'], new_grid['lap'], new_grid['number_stops'])

        # Override whole grid
        self.timing.set_grid(copy.deepcopy(new_timing.get_grid()))

    def _update_stats(self, new_timing: Timing):
        stats = self.timing.get_stats()
        new_stats = new_timing.get_stats()
        if stats['stage'] != new_stats['stage']:
            self._update_stat('stage', new_stats['stage'])

        # Override (some) stats
        stats['stage'] = new_stats['stage']

    def _update_stat(self, stat_name, value):
        path = '/v1/events/%s/stats/%s' % (self.event_name, stat_name)
        data = {'value': value}
        self.api.put(path, data)

    def _add_time(self, team_name, time, gap, lap, number_stops):
        path = '/v1/events/%s/timing' % (self.event_name)
        data = {
            'team_name': team_name,
            'time': time,
            'gap': gap,
            'lap': lap,
            'number_stops': number_stops
        }
        self.api.post(path, data)

    def _add_team(self, team_name, team_number):
        path = '/v1/events/%s/teams' % (self.event_name)
        data = {
            'name': team_name,
            'number': team_number,
            'drivers': [],
            'reference_time_offset': 0
        }
        self.api.post(path, data)

    def _update_team_name(self, old_team_name, new_team_name):
        path = '/v1/events/%s/teams/%s' % (self.event_name, old_team_name)
        data = {'name': new_team_name}
        self.api.put(path, data)

    def _update_team_number(self, team_name, team_number):
        path = '/v1/events/%s/teams/%s' % (self.event_name, team_name)
        data = {'number': team_number}
        self.api.put(path, data)
