import json
import threading
import time
import requests

class HealthWorker(threading.Thread):
    def __init__(self, parent, api_requests, event_name: str, *args, **kwargs):
        self._parent = parent
        self._api_requests = api_requests
        self._event_name = event_name
        
        self.HEALTH_CATEGORY = 'crawler'
        self.WAIT_TIME = 20
        self.WARNING_RATIO = 10
        self.ERROR_RATIO = 50

        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            try:
                health_stats = self._parent.get_health_stats()
                
                api_requests = health_stats['api_requests']
                api_errors = health_stats['api_errors']
                api_ratio = api_errors / api_requests * 100 if api_requests > 0 else 0
                if api_errors == 0:
                    api_errors_str = ''
                else:
                    api_errors_str = 'Hubo %d de %d peticiones erróneas a la API (%.2f)' % (api_errors, api_requests, api_ratio)
                
                number_messages = health_stats['number_messages']
                error_messages = health_stats['error_messages']
                messages_ratio = error_messages / number_messages * 100 if number_messages > 0 else 0
                if error_messages == 0:
                    error_messages_str = ''
                else:
                    error_messages_str = 'Hubo %d de %d mensajes sin analizar (%.2f)' % (error_messages, number_messages, messages_ratio)
                
                response = self._api_requests.put(
                    '/v1/events/%s/health/%s/api_connection' % (self._event_name, self.HEALTH_CATEGORY),
                    {'status': self._get_status(api_ratio), 'message': api_errors_str}
                )
                if 'error' in response:
                    print('ERROR HEALTH')
                    print(response)
                
                response = self._api_requests.put(
                    '/v1/events/%s/health/%s/parse_timing' % (self._event_name, self.HEALTH_CATEGORY),
                    {'status': self._get_status(api_ratio), 'message': error_messages_str}
                )
                if 'error' in response:
                    print('ERROR HEALTH')
                    print(response)
                
            except Exception as e:
                print('ERROR: Cannot update health stats!')
                print(str(e))
            finally:
                time.sleep(self.WAIT_TIME)

    def _get_status(self, ratio):
        if ratio < self.WARNING_RATIO:
            return 'ok'
        elif ratio < self.ERROR_RATIO:
            return 'warning'
        else:
            return 'error'
