import requests
import json

class ApiRequests:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.api_token = api_token

    def get(self, path: str):
        headers = {'X-Request-Id': self.api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self.base_url, path)
        r = requests.get(url, headers=headers)
        return json.loads(r.content)

    def post(self, path: str, data):
        headers = {'X-Request-Id': self.api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self.base_url, path)
        r = requests.post(url, json=data, headers=headers)
        return json.loads(r.content)

    def put(self, path: str, data):
        headers = {'X-Request-Id': self.api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self.base_url, path)
        r = requests.put(url, json=data, headers=headers)
        return json.loads(r.content)
