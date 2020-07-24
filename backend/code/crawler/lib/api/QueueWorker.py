from .RequestWorker import RequestWorker

import random
import json
import threading
import time
import requests

class QueueWorker(threading.Thread):
    def __init__(self, parent, max_workers_primary: int, max_workers_secondary: int,
                 base_url: str, api_token: str, *args, **kwargs):
        self._parent = parent
        self._max_workers_primary = max_workers_primary
        self._max_workers_secondary = max_workers_secondary
        self._base_url = base_url
        self._api_token = api_token
        
        self._request_workers_primary = {}
        self._request_workers_secondary = {}
        
        super().__init__(*args, **kwargs)

    def run(self):
        i = 1
        wait = False
        
        while True:
            if wait:
                time.sleep(1)
                wait = False
            
            if len(self._request_workers_primary) < self._max_workers_primary:
                primary_queue, secondary_queue = self._parent.get_queues()
                if len(primary_queue) == 0:
                    pass
                else:
                    self._run_queue_item(1, primary_queue)
            
            if len(self._request_workers_secondary) < self._max_workers_secondary:
                secondary_queue, secondary_queue = self._parent.get_queues()
                if len(secondary_queue) == 0:
                    pass
                else:
                    self._run_queue_item(2, secondary_queue)
            
            i = i + 1
    
    def _run_queue_item(self, priority: int, queue):
        item = queue.pop(0)
        key = '%s_%s_%s' % (item['method'], item['path'], random.randint(0, 1000))
        worker = RequestWorker(self, key, priority, self._base_url, self._api_token, item)
        
        if priority == 1:
            self._request_workers_primary[key] = worker
        elif priority == 2:
            self._request_workers_secondary[key] = worker
        
        worker.start()

        self._parent.set_queue(priority, queue)            
    
    def get_parent(self):
        return self._parent
    
    def get_number_workers(self):
        return len(self._request_workers_primary) + len(self._request_workers_secondary)
    
    def done_worker(self, key: str, priority: int):
        try:
            if priority == 1:
                del self._request_workers_primary[key]
            elif priority == 2:
                del self._request_workers_secondary[key]
        except:
            pass
