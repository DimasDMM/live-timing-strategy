import requests
import json

class ApiRequests:
    def __init__(self, base_url: str, debug = False):
        self.debug = debug

        # Settings
        self.base_url = base_url
        self._load_settings()

    def get(self, path):
        api_token = self.settings['api_token']
        headers = {'X-Request-Id': api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self.base_url, path)
        r = requests.get(url, headers=headers)
        return json.loads(r.content)

    def post(self, path, data):
        api_token = self.settings['api_token']
        headers = {'X-Request-Id': api_token, 'Content-Type': 'application/json; charset=utf-8'}
        url = '%s%s' % (self.base_url, path)
        r = requests.post(url, json=data, headers=headers)
        return json.loads(r.content)

    def put(self, path, data):
        pass

    def _load_settings(self):
        if self.file_settings is not None:
            try:
                with open(self.file_settings, 'r') as fp:
                    self.settings = json.load(fp)
            except Exception as e:
                print('Error: %s' % str(e))
                raise e
