from .ApiRequests import ApiRequests
from .health.HealthWorker import HealthWorker
from .MessagesParser import MessagesParser
from .TimingUpdater import TimingUpdater
from .Timing import Timing
from .WebSocketListener import WebSocketListener
from .WebSocketParser import WebSocketParser

from datetime import datetime
import json
import os
import random
import time
import websocket

class Crawler:
    # Constants
    TEMP_FILE_TIMING = 'temp_timing.json'
    GET_STATS_INTERVAL = 50
    MAX_WORKERS_PRIMARY = 15
    MAX_WORKERS_SECONDARY = 15
    API_URL = 'http://nginx'
    WS_URL = 'ws://www.apex-timing.com:8092'
    
    def __init__(self, event_name: str, api_token: str, base_path: str, messages_path: str,
                 errors_path: str, use_websocket_listener=True, stop_if_error=False, reset_last=False):
        self.event_name = event_name
        self.api_token = api_token
        self.base_path = base_path
        self.errors_path = errors_path
        self.stop_if_error = stop_if_error
        
        if reset_last:
            self.save_last_timing(Timing())
        
        # Init health stats
        self.RESET_HEALTH_COUNTER = 1000
        self.health_stats = {
            'number_messages': 0,
            'error_messages': 0,
            'api_requests': 0,
            'api_errors': 0
        }
        
        # Build initial objects
        self.timing = self.get_last_timing()
        self.api_requests = ApiRequests(self, self.API_URL, api_token, self.MAX_WORKERS_PRIMARY, self.MAX_WORKERS_SECONDARY)
        messages_parser = MessagesParser(self.timing, self.api_requests)
        
        messages_path = '%s/%s' % (self.base_path, messages_path)
        if use_websocket_listener:
            self.ws = WebSocketListener(self.WS_URL, messages_parser, messages_path)
        else:
            self.ws = WebSocketParser(messages_parser, messages_path)
        
        self._health_worker = HealthWorker(self, self.api_requests, event_name)
        self._health_worker.start()
        
        # Get configuration of event
        print('Setting initial variables...')
        configuration_url_path = '/v1/events/%s/configuration' % (event_name)
        configuration = self.api_requests.get(configuration_url_path)
        if 'error' in configuration:
            raise Exception(configuration)

        configuration = {x['name']:x['value'] for x in configuration['data']}
        self.timing.set_configuration(configuration)
        
        stats = self.get_stats()
        self.timing.set_stats(stats)
        
        # Timing updater class
        self.updater = TimingUpdater(self.api_requests, event_name, configuration, self.timing)
    
    def run(self):
        message_i = 0
        self.api_requests.run()
        
        while True:
            message_i = message_i + 1

            print('#' * 20)
            stats = self.timing.get_stats()
            
            # Get stats every X number of messages
            if message_i % self.GET_STATS_INTERVAL == 0:
                print('Reloading event stats...')
                self.get_stats_future()
                self.get_configuration_future()
            
            # Skip if status is offline or stage is "pause"
            if stats['status'] == 'offline':
                print('Event status is offline or stage is paused')
                time.sleep(5)
                continue

            print('Status: %s - Stage: %s' % (stats['status'], stats['stage']))
            
            q_total, q1, q2 = self.api_requests.get_number_in_queue()
            n_workers = self.api_requests.get_number_workers()
            print('In queue: %d (prim: %d - sec: %d) - Workers: %d' % (q_total, q1, q2, n_workers))

            try:
                self.timing = self.ws.run()
            except Exception as e:
                data = str(e)
                print(data)

                with open('%s/%s/%s' % (self.base_path, self.errors_path, self.get_random_filename()), 'w') as fp:
                    fp.write(data)

                if self.stop_if_error:
                    print('STOP!')
                    exit(0)
                else:
                    continue
            
            if self.timing is None:
                if q_total > 0 or n_workers > 0:
                    print('No more messages! Waiting for workers...')
                    time.sleep(1)
                    continue
                else:
                    print('No more messages!')
                    print('Time: %s' % datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                    self.update_status('offline')
                    exit(0)

            print('Updating data...')
            try:
                self.updater.update_timing(self.timing)
                self.save_last_timing()
            except Exception as e:
                print(self.timing.to_object())
                raise e
    
    def get_health_stats(self):
        return self.health_stats
    
    def add_health_stat(self, name: str, reset=True):
        if reset and name in ['error_messages', 'number_messages'] and self.health_stats['number_messages'] >= self.RESET_HEALTH_COUNTER:
            self.health_stats['error_messages'] = 0
            self.health_stats['number_messages'] = 0
        elif reset and name in ['api_errors', 'api_requests'] and self.health_stats['api_requests'] >= self.RESET_HEALTH_COUNTER:
            self.health_stats['api_errors'] = 0
            self.health_stats['api_requests'] = 0
        else:
            self.health_stats[name] = self.health_stats[name] + 1
    
    def get_stats(self):
        stats_url_path = '/v1/events/%s/stats' % (self.event_name)
        stats = self.api_requests.get(stats_url_path)
        stats = {x['name']:x['value'] for x in stats['data']}
        return stats

    def get_stats_future(self):
        def callback(response, params):
            stats = {x['name']:x['value'] for x in response['data']}
            params['timing'].set_stats(stats)
        
        url_path = '/v1/events/%s/stats' % (self.event_name)
        self.api_requests.get_future(url_path, priority=1, callback=callback, callback_params={'timing': self.timing})

    def get_configuration_future(self):
        def callback(response, params):
            configuration = {x['name']:x['value'] for x in response['data']}
            params['timing'].set_configuration(configuration)

        url_path = '/v1/events/%s/configuration' % (self.event_name)
        self.api_requests.get_future(url_path, priority=2, callback=callback, callback_params={'timing': self.timing})

    def update_status(self, value: str):
        path = '/v1/events/%s/stats/status' % (self.event_name)
        data = {'value': value}
        response = self.api_requests.put(path, data)
        if 'error' in response:
            raise Exception(response)

    def get_last_timing(self):
        file_path = '%s/%s' % (self.base_path, self.TEMP_FILE_TIMING)
        
        if not os.path.isfile(file_path):
            timing = Timing()
            self.save_last_timing(timing)
            return timing

        try:
            with open(file_path, 'r') as fp:
                return Timing().from_dict(json.load(fp))
        except:
            timing = Timing()
            self.save_last_timing(timing)
            return timing

    def save_last_timing(self, timing=None):
        file_path = '%s/%s' % (self.base_path, self.TEMP_FILE_TIMING)
        timing = self.timing if timing is None else timing

        try:
            with open(file_path, 'w') as fp:
                json.dump(timing.to_object(), fp, indent=4)
        except Exception as e:
            print('Error: %s' % str(e))
            raise e

    def get_random_filename(self):
        current_time = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S.%f')
        return '%s_rd%d.txt' % (current_time, random.randint(0, 100))

    def close(self):
        print('Closing...')
        exit(0)
