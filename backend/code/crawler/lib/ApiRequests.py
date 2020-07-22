import json
import requests
import threading

from .api.QueueWorker import QueueWorker

class ApiRequests:
    def __init__(self, base_url: str, api_token: str, max_workers_primary=10, max_workers_secondary=5):
        self._base_url = base_url
        self._api_token = api_token
        self._max_workers_primary = max_workers_primary
        self._max_workers_secondary = max_workers_secondary
        
        self._primary_queue = {}
        self._secondary_queue = {}
        
        self._queue_worker = None
        self._locks = {
            'queues': threading.Lock(),
            'workers': threading.Lock()
        }

    def run(self):
        if self._queue_worker is not None and self._queue_worker.is_alive():
            return
        
        self._queue_worker = QueueWorker(self, self._max_workers_primary, self._max_workers_secondary,
                                         self._base_url, self._api_token)
        self._queue_worker.start()
    
    def lock(self, lock_name):
        return self._locks[lock_name]
    
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
        return json.loads(r.content)

    def post(self, path: str, data):
        """Request which is not handled by a worker"""
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.post(url, json=data, headers=headers)
        return json.loads(r.content)

    def put(self, path: str, data):
        """Request which is not handled by a worker"""
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.put(url, json=data, headers=headers)
        return json.loads(r.content)
    
    def get_future(self, path, priority=1, callback=None, callback_params=None):
        self._add_request(priority, 'get', path, None, callback, callback_params)
    
    def post_future(self, path, data, priority=1, callback=None, callback_params=None):
        self._add_request(priority, 'post', path, data, callback, callback_params)
    
    def put_future(self, path, data, priority=1, callback=None, callback_params=None):
        self._add_request(priority, 'put', path, data, callback, callback_params)

    def _add_request(self, priority: int, method: str, path: str, data, callback, callback_params):
        with self.lock('queues'):
            request = {
                'method': method,
                'path': path,
                'data': data,
                'callback': callback,
                'callback_params': callback_params
            }
            key = '%s_%s_%s' % (method, path, json.dumps(data))
            if priority == 1:
                self._primary_queue[key] = request
            elif priority == 2:
                self._secondary_queue[key] = request
