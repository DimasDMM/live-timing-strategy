import json
import requests

from .api.QueueWorker import QueueWorker

class ApiRequests:
    def __init__(self, parent, base_url: str, api_token: str,
                 max_workers_primary=10, max_workers_secondary=5):
        self._parent = parent
        self._base_url = base_url
        self._api_token = api_token
        self._max_workers_primary = max_workers_primary
        self._max_workers_secondary = max_workers_secondary
        
        self._primary_queue = []
        self._secondary_queue = []
        self._queue_worker = QueueWorker(self, self._max_workers_primary, self._max_workers_secondary,
                                         self._base_url, self._api_token)
        
        self._number_requests = 0
        self._number_errors = 0

    def run(self):
        self._queue_worker.start()
    
    def is_alive(self):
        return self._queue_worker is not None and self._queue_worker.is_alive()
    
    def get_queues(self):
        return self._primary_queue, self._secondary_queue
    
    def get_number_in_queue(self):
        q1 = len(self._primary_queue)
        q2 = len(self._secondary_queue)
        return q1 + q2, q1, q2

    def get_number_workers(self):
        return self._queue_worker.get_number_workers()

    def set_queue(self, priority: int, queue):
        if priority == 1:
            self._primary_queue = queue
        elif priority == 2:
            self._secondary_queue = queue

    def get(self, path: str):
        """Request which is not handled by a worker"""
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.get(url, headers=headers)
        response = json.loads(r.content)

        self.add_request_counter()
        if 'error' in response:
            print('ERROR REQUEST')
            print(response)
            self.add_error_counter()

        return response

    def post(self, path: str, data):
        """Request which is not handled by a worker"""
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.post(url, json=data, headers=headers)
        response = json.loads(r.content)

        self.add_request_counter()
        if 'error' in response:
            print('ERROR REQUEST')
            print(data)
            print(response)
            self.add_error_counter()

        return response

    def put(self, path: str, data):
        """Request which is not handled by a worker"""
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.put(url, json=data, headers=headers)
        response = json.loads(r.content)

        self.add_request_counter()
        if 'error' in response:
            print('ERROR REQUEST')
            print(data)
            print(response)
            self.add_error_counter()

        return response
    
    def get_future(self, path, priority=1, callback=None, callback_params=None):
        self._add_request(priority, 'get', path, None, callback, callback_params)
    
    def post_future(self, path, data, priority=1, callback=None, callback_params=None):
        self._add_request(priority, 'post', path, data, callback, callback_params)
    
    def put_future(self, path, data, priority=1, callback=None, callback_params=None):
        self._add_request(priority, 'put', path, data, callback, callback_params)

    def add_request_counter(self):
        self._parent.add_health_stat('api_requests')

    def add_error_counter(self):
        self._parent.add_health_stat('api_errors')

    def _add_request(self, priority: int, method: str, path: str, data, callback, callback_params):
        request = {
            'method': method,
            'path': path,
            'data': data,
            'callback': callback,
            'callback_params': callback_params
        }
        if priority == 1:
            self._primary_queue.append(request)
        elif priority == 2:
            self._secondary_queue.append(request)
