import websocket
import os
import time
from datetime import datetime
import random
import json

from lib.Timing import Timing
from lib.MessagesParser import MessagesParser
from lib.ApiRequests import ApiRequests
from lib.WebSocketListener import WebSocketListener
from lib.WebSocketParser import WebSocketParser
from lib.TimingUpdater import TimingUpdater

try:
    import thread
except ImportError:
    import _thread as thread

EVENT_NAME = 'Resistencia%20Los%20Santos%2018-07-2020'
WS_URL = 'ws://www.apex-timing.com:8092'
API_URL = 'http://nginx'
API_TOKEN = 'd265aed699f7409ac0ec6fe07ee9cb11'

TEMP_FILE_TIMING = 'temp_timing.json'
MESSAGES_PATH = '../../artifacts/logs/se_race'
GET_STATS_INTERVAL = 50
MAX_WORKERS_PRIMARY = 15
MAX_WORKERS_SECONDARY = 15

STOP_IF_ERROR = False
ERRORS_PATH = '../../artifacts/logs/errors'

def create_dir(path):
    current_path = os.path.dirname(os.path.realpath(__file__))
    abs_path = current_path + '/' + path
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)

def get_last_timing():
    if not os.path.isfile(TEMP_FILE_TIMING):
        timing = Timing()
        save_last_timing(timing.to_object())

    try:
        with open(TEMP_FILE_TIMING, 'r') as fp:
            return Timing().from_dict(json.load(fp))
    except Exception as e:
        print('Error: %s' % str(e))
        raise e

def save_last_timing(timing: Timing):
    try:
        with open(TEMP_FILE_TIMING, 'w') as fp:
            json.dump(timing.to_object(), fp, indent=4)
    except Exception as e:
        print('Error: %s' % str(e))
        raise e

def get_stats(api_requests: ApiRequests, event_name: str):
    stats_url_path = '/v1/events/%s/stats' % (event_name)
    stats = api_requests.get(stats_url_path)
    stats = {x['name']:x['value'] for x in stats['data']}
    return stats

def get_stats_future(api_requests: ApiRequests, event_name: str, timing: Timing):
    def callback(response, params):
        stats = {x['name']:x['value'] for x in response['data']}
        params['timing'].set_stats(stats)
    
    stats_url_path = '/v1/events/%s/stats' % (event_name)
    api_requests.get_future(stats_url_path, priority=1, callback=callback, callback_params={'timing': timing})

def update_status(api_requests: ApiRequests, event_name: str, value: str):
    path = '/v1/events/%s/stats/status' % (event_name)
    data = {'value': value}
    response = api_requests.put(path, data)
    if 'error' in response:
        raise Exception(response)

def get_random_filename():
    current_time = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S.%f')
    return '%s_rd%d.txt' % (current_time, random.randint(0, 100))

if __name__ == '__main__':
    create_dir(ERRORS_PATH)
    
    save_last_timing(Timing()) # To do: debug, remove
    timing = get_last_timing()

    # Build initial objects
    api_requests = ApiRequests(API_URL, API_TOKEN, MAX_WORKERS_PRIMARY, MAX_WORKERS_SECONDARY)
    messages_parser = MessagesParser(timing, api_requests)
    #ws = WebSocketListener(WS_URL, messages_parser, MESSAGES_PATH)
    ws = WebSocketParser(messages_parser, MESSAGES_PATH)
    
    # Get configuration of event
    print('Setting initial variables...')
    configuration_url_path = '/v1/events/%s/configuration' % (EVENT_NAME)
    configuration = api_requests.get(configuration_url_path)

    if 'error' in configuration:
        raise Exception(configuration)

    configuration = {x['name']:x['value'] for x in configuration['data']}
    timing.set_configuration(configuration)
    
    stats = get_stats(api_requests, EVENT_NAME)
    timing.set_stats(stats)

    # Timing updater class
    updater = TimingUpdater(api_requests, EVENT_NAME, configuration, timing)

    # Start crawling process
    message_i = 0
    while True:
        message_i = message_i + 1

        print('#' * 20)
        stats = timing.get_stats()
        
        # Init requests worker (if it is not alive)
        api_requests.run()
        
        # Get stats every X number of messages
        if message_i % GET_STATS_INTERVAL == 0:
            print('Reloading event stats...')
            get_stats_future(api_requests, EVENT_NAME, timing)
        
        # Skip if status is offline or stage is "pause"
        if stats['status'] == 'offline':
            print('Event status is offline or stage is paused')
            time.sleep(5)
            continue

        print('Status: %s - Stage: %s' % (stats['status'], stats['stage']))
        
        q_total, q1, q2 = api_requests.get_number_in_queue()
        n_workers = api_requests.get_number_workers()
        print('In queue: %d (prim: %d - sec: %d) - Workers: %d' % (q_total, q1, q2, n_workers))

        try:
            ws_timing = ws.run()
        except Exception as e:
            data = str(e)
            print(data)

            with open('%s/%s' % (ERRORS_PATH, get_random_filename()), 'w') as fp:
                fp.write(data)

            if STOP_IF_ERROR:
                print('STOP!')
                exit(0)
            else:
                continue
        
        if ws_timing is None:
            if q_total > 0 or n_workers > 0:
                print('No more messages! Waiting for workers...')
                continue
            else:
                print('No more messages!')
                update_status(api_requests, EVENT_NAME, 'offline')
                exit(0)

        print('Updating data...')
        try:
            updater.update_timing(ws_timing)
            save_last_timing(ws_timing)
        except Exception as e:
            print(ws_timing.to_object())
            raise e
