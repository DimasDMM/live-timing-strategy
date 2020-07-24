import copy
import time

from .ApiRequests import ApiRequests
from .Timing import Timing

class TimingUpdater:
    def __init__(self, api: ApiRequests, event_name: str, event_config: list, timing: Timing):
        self._api_requests = api
        self._event_name = event_name
        self._event_config = event_config
        self._timing = copy.deepcopy(timing)

    def update_timing(self, new_timing: Timing):
        self._update_stats(new_timing)
        self._update_grid(new_timing)

    def _update_grid(self, new_timing: Timing):
        # Api updates
        grid = self._timing.get_grid()
        stats = self._timing.get_stats()

        new_grid = copy.deepcopy(new_timing.get_grid())

        for team_key, team_data in new_grid.items():
            if team_key not in grid:
                # Add new team
                self._add_team(team_data['team_name'], team_data['team_number'])
            elif team_data['team_name'] is not None:
                if grid[team_key]['team_name'] != team_data['team_name']:
                    # Update team name
                    self._update_team_name(grid[team_key]['team_name'], team_data['team_name'])
                if grid[team_key]['team_number'] != team_data['team_number']:
                    # Update team number
                    self._update_team_number(team_data['team_name'], team_data['team_number'])

                if team_data['in_box'] and not grid[team_key]['in_box']:
                    # Driver entered to box
                    self._add_kart_in_box(team_data['team_name'])

                if grid[team_key]['lap'] != team_data['lap'] and team_data['lap'] > 0:
                    # New time of the team
                    self._add_time(
                        team_data['position'],
                        team_data['team_name'],
                        team_data['time'],
                        team_data['best_time'],
                        team_data['interval'],
                        team_data['interval_unit'],
                        team_data['lap'],
                        team_data['number_stops']
                    )
                elif stats['stage'] == 'classification' and grid[team_key]['lap'] > 0 and grid[team_key]['interval'] != team_data['interval']:
                    # Update last time
                    self._update_time(
                        team_data['position'],
                        team_data['team_name'],
                        team_data['time'],
                        team_data['best_time'],
                        team_data['interval'],
                        team_data['interval_unit'],
                        team_data['lap'],
                        team_data['number_stops']
                    )
                    # To do: Delete previous time

            # Driving time may be empty if the driver is in box
            if team_data['driving_time'] is None and team_key in grid:
                team_data['driving_time'] = grid[team_key]['driving_time']

            if 'drivers' in team_data:
                for driver_name in team_data['drivers'].keys():
                    if team_key not in grid or driver_name not in grid[team_key]['drivers']:
                        # Add new driver and set driving time
                        self._add_driver(team_data['team_name'], driver_name)
                        old_driving_time = 0
                    else:
                        old_driving_time = grid[team_key]['drivers'][driver_name]['driving_time']
                    
                    new_driving_time = team_data['drivers'][driver_name]['driving_time']                    
                    if new_driving_time > 0 and new_driving_time != old_driving_time:
                        # Update driving time
                        self._update_driver(team_data['team_name'], driver_name, new_driving_time)

        # Override whole grid
        self._timing.set_grid(new_grid)

    def _update_stats(self, new_timing: Timing):
        stats = self._timing.get_stats()
        new_stats = new_timing.get_stats()
        if 'stage' in new_stats and stats['stage'] != new_stats['stage']:
            self._wait_no_workers()
            self._update_stat('stage', new_stats['stage'], 1)
            stats['stage'] = new_stats['stage']
        if 'remaining_event' in new_stats and stats['remaining_event'] != new_stats['remaining_event']:
            self._update_stat('remaining_event', new_stats['remaining_event'], 2)
            stats['remaining_event'] = new_stats['remaining_event']
        if 'remaining_event_unit' in new_stats and stats['remaining_event_unit'] != new_stats['remaining_event_unit']:
            self._update_stat('remaining_event_unit', new_stats['remaining_event_unit'], 2)
            stats['remaining_event_unit'] = new_stats['remaining_event_unit']

        self._timing.set_stats(stats)

    def _update_stat(self, name: str, value, priority: int):
        print('- Updating "%s" to "%s"...' % (name, value))
        path = '/v1/events/%s/stats/%s' % (self._event_name, name)
        data = {'value': value}
        if priority == 1:
            response = self._api_requests.put(path, data)
            if 'error' in response:
                raise Exception(response)
        elif priority == 2:
            self._api_requests.put_future(path, data, priority)

    def _add_kart_in_box(self, team_name: str):
        def _callback_box(response, callback_params):
            print('RESPONSE KART IN BOX')
            print(response)
        
        print('- Team "%s" entered to box...' % (team_name))
        path = '/v1/events/%s/karts-box/in' % (self._event_name)
        data = {'team_name': team_name}
        self._api_requests.post_future(path, data, 1, callback=_callback_box)

    def _add_time(self, position: int, team_name: str, time: int, best_time: int,
                  interval: int, interval_unit: str, lap: int, number_stops: int):
        print('- Adding time of team "%s"...' % (team_name))
        path = '/v1/events/%s/timing' % (self._event_name)
        data = {
            'position': position,
            'team_name': team_name,
            'time': time,
            'best_time': best_time,
            'interval': interval,
            'interval_unit': interval_unit,
            'lap': lap,
            'number_stops': number_stops
        }
        self._api_requests.post_future(path, data, 1)

    def _update_time(self, position: int, team_name: str, time: int, best_time: int,
                     interval: int, interval_unit: str, lap: int, number_stops: int):
        print('- Re-adding last time of team "%s"...' % (team_name))
        path = '/v1/events/%s/timing' % (self._event_name)
        data = {
            'position': position,
            'team_name': team_name,
            'time': time,
            'best_time': best_time,
            'interval': interval,
            'interval_unit': interval_unit,
            'lap': lap,
            'number_stops': number_stops
        }
        self._api_requests.post_future(path, data, 1)

    def _add_team(self, team_name: str, team_number: int):
        print('- Adding team "%s"...' % (team_name))
        path = '/v1/events/%s/teams' % (self._event_name)
        data = {
            'name': team_name,
            'number': team_number,
            'drivers': [],
            'reference_time_offset': 0
        }
        response = self._api_requests.post(path, data)
        if 'error' in response:
            raise Exception(response)

    def _update_team_name(self, old_team_name: str, new_team_name: str):
        print('- Updating team name "%s" to "%s"...' % (old_team_name, new_team_name))
        path = '/v1/events/%s/teams/%s' % (self._event_name, old_team_name)
        data = {'name': new_team_name}
        response = self._api_requests.put(path, data)
        if 'error' in response:
            raise Exception(response)

    def _update_team_number(self, team_name: str, team_number: int):
        print('- Updating team number "%s" to "%d"...' % (team_name, team_number))
        path = '/v1/events/%s/teams/%s' % (self._event_name, team_name)
        data = {'number': team_number}
        self._api_requests.put_future(path, data, 2)

    def _add_driver(self, team_name: str, driver_name: str):
        print('- Adding driver "%s" to the team "%s"...' % (driver_name, team_name))
        path = '/v1/events/%s/teams/%s/%s' % (self._event_name, team_name, driver_name)
        data = {}
        self._api_requests.post_future(path, data, 2)

    def _update_driver(self, team_name: str, driver_name: str, driving_time: int):
        print('- Updating driver "%s" of team "%s"...' % (driver_name, team_name))
        path = '/v1/events/%s/teams/%s/%s' % (self._event_name, team_name, driver_name)
        data = {'driving_time': driving_time}
        self._api_requests.put_future(path, data, 2)

    def _wait_no_workers(self):
        while True:
            q_total, _, _ = self._api_requests.get_number_in_queue()
            n_workers = self._api_requests.get_number_workers()
            if q_total > 0 or n_workers > 0:
                print('Waiting queue empty... (%d in queue, %d workers)' % (q_total, n_workers))
                time.sleep(0.5)
            else:
                break
