import websocket
import os
import time
from datetime import datetime
import random
import json

from lib.Timing import Timing
from lib.WebSocketParser import WebSocketParser
from lib.ApiRequests import ApiRequests
from lib.WebSocket import WebSocket
from lib.WebSocketSim import WebSocketSim
from lib.TimingUpdater import TimingUpdater

try:
    import thread
except ImportError:
    import _thread as thread

FILE_SETTINGS = 'settings.json'
FILE_TIMING = 'temp_timing.json'

def get_settings():
    try:
        with open(FILE_SETTINGS, 'r') as fp:
            return json.load(fp)
    except Exception as e:
        print('Error: %s' % str(e))
        raise e

def get_last_timing():
    if not os.path.isfile(FILE_TIMING):
        timing = Timing()
        save_last_timing(timing.to_object())

    try:
        with open(FILE_TIMING, 'r') as fp:
            return Timing().from_dict(json.load(fp))
    except Exception as e:
        print('Error: %s' % str(e))
        raise e

def save_last_timing(timing):
    try:
        with open(FILE_TIMING, 'w') as fp:
            json.dump(timing, fp, indent=4)
    except Exception as e:
        print('Error: %s' % str(e))
        raise e

if __name__ == '__main__':
    settings = get_settings()

    timing = get_last_timing()

    # Build initial objects
    api_requests = ApiRequests(settings['api_url'], settings['api_token'])
    ws_parser = WebSocketParser(timing, api_requests)
    #ws = WebSocket(settings['ws_url'], ws_parser, save_messages=settings['save_messages'])
    ws = WebSocketSim(settings['ws_url'], ws_parser, '../../artifacts/logs/se_combined/*.txt')
    
    # Get configuration of event
    configuration_url_path = '/v1/events/%s/configuration' % (settings['event_name'])
    configuration = api_requests.get(configuration_url_path)
    configuration = {x['name']:x['value'] for x in configuration['data']}
    timing.set_configuration(configuration)

    # Timing updater class
    updater = TimingUpdater(api_requests, settings['event_name'], configuration, timing)

    # Start crawling process
    while True:
        print('#' * 20)
        settings = get_settings()
        
        print('Getting event stats...')
        stats_url_path = '/v1/events/%s/stats' % (settings['event_name'])
        stats = api_requests.get(stats_url_path)
        stats = {x['name']:x['value'] for x in stats['data']}
        timing.set_stats(stats)
        
        # Skip if status is offline or stage is "pause"
        if stats['status'] == 'offline':
            print('Event status is offline or stage is paused')
            time.sleep(5)
            continue

        print('Status: %s - Stage: %s' % (stats['status'], stats['stage']))

        ws_timing = ws.run()
        if ws_timing is None:
            print('Finished!')
            # To do: set event offline

        print(timing.to_object()) # To do: remove, debug

        updater.update_timing(timing)
        save_last_timing(timing)
