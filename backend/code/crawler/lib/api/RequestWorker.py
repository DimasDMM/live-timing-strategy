import json
import threading
import time
import requests

class RequestWorker(threading.Thread):
    def __init__(self, parent, key: str, priority: int, base_url: str,
                 api_token: str, request_data, *args, **kwargs):
        self._parent = parent
        self._key = key
        self._priority = priority
        self._base_url = base_url
        self._api_token = api_token
        self._request_data = request_data

        super().__init__(*args, **kwargs)

    def run(self):
        try:
            if self._request_data['method'] == 'get':
                response = self._get(self._request_data['path'])
            elif self._request_data['method'] == 'post':
                response = self._post(self._request_data['path'], self._request_data['data'])
            elif self._request_data['method'] == 'put':
                response = self._put(self._request_data['path'], self._request_data['data'])
            
            if self._request_data['callback'] is not None:
                self._request_data['callback'](response, self._request_data['callback_params'])
        except Exception as e:
            print(str(e))
        finally:
            self._parent.done_worker(self._key, self._priority)
    
    def _get(self, path: str):
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.get(url, headers=headers)
        response = json.loads(r.content)

        self._add_request_counter()
        if 'error' in response:
            print('ERROR REQUEST')
            print(response)
            self._add_error_counter()
        
        return response

    def _post(self, path: str, data):
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.post(url, json=data, headers=headers)
        response = json.loads(r.content)

        self._add_request_counter()
        if 'error' in response:
            print('ERROR REQUEST')
            print(data)
            print(response)
            self._add_error_counter()
        
        return response

    def _put(self, path: str, data):
        headers = {'X-Request-Id': self._api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self._base_url, path)
        r = requests.put(url, json=data, headers=headers)
        response = json.loads(r.content)

        self._add_request_counter()
        if 'error' in response:
            print('ERROR REQUEST')
            print(data)
            print(response)
            self._add_error_counter()
        
        return response

    def _add_request_counter(self):
        self._parent.get_parent().add_request_counter()

    def _add_error_counter(self):
        self._parent.get_parent().add_error_counter()
