import websocket
import os
import time
from datetime import datetime
import random
import json

from lib.TimingParser import TimingParser
from lib.ApiRequests import ApiRequests
from lib.WebSocket import WebSocket
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
    if os.path.isfile(FILE_TIMING):
        save_last_timing([])

    try:
        with open(FILE_TIMING, 'r') as fp:
            return json.load(fp)
    except Exception as e:
        print('Error: %s' % str(e))
        raise e
    else:
        return []

def save_last_timing(timing):
    try:
        with open(FILE_TIMING, 'w') as fp:
            json.dump(timing, fp, indent=4)
    except Exception as e:
        print('Error: %s' % str(e))
        raise e

if __name__ == '__main__':
    settings = get_settings()

    last_timing = get_last_timing()
    
    # Get configuration of event
    configuration_url_path = '/v1/events/%s/configuration' % (settings['event_name'])
    configuration = api_requests.get(configuration_url_path)
    configuration = {x['name']:x['value'] for x in configuration['data']}

    # Build objects
    api_requests = ApiRequests(settings['api_url'])
    parser = TimingParser(last_timing, api_requests)
    ws = WebSocket(settings['ws_url'], parser, save_messages=settings['save_messages'])

    updater = TimingUpdater(api_requests, settings['event_name'], configuration, last_timing)

    # Start crawling process
    while True:
        print('#' * 20)
        settings = get_settings()
        
        print('Getting event stats...')
        stats_url_path = '/v1/events/%s/stats' % (settings['event_name'])
        stats = api_requests.get(stats_url_path)
        stats = {x['name']:x['value'] for x in stats['data']}
        
        # Skip if status is offline or stage is "pause"
        if stats['status'] == 'offline' or stats['stage'] in ['pause', 'unknown']:
            print('Event status is offline or stage is paused')
            time.sleep(5)
            continue

        print('Status: %s - Stage: %s' % (stats['status'], stats['stage']))

        #ws.run()
        ## Debug ##
        with open('../../artifacts/logs/race/test_grid.txt', 'r') as fp:
            message = fp.read()
            parser.on_message(message)
        ## -- ##

        exit(0)

        timing = parser.get_timing()
        save_last_timing(timing)

        updater.update_timing(timing, stats)

        path = '/v1/events/%s/timing' % (settings['event_name'])
        for row in data:
            api.post(path, row)
