"""
Library to easily create a client that connects to a cred-server API server.

"""
import urllib.request
import urllib.error
import http.cookiejar
import json
import threading
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s][%(asctime)s] %(message)s',
    datefmt='%d/%m/%Y-%H:%M:%S'
)


def request_wrapper(req):
    """Wrapper around requests to handle error codes."""
    try:
        return req
    except urllib.error.HTTPError as e:
        if e.code == 401:
            msg = 'Unauthorized'
        elif e.code == 404:
            msg = 'Not Found'
        else:
            msg = 'Unknown Error'
        logging.debug(
            'ERROR: Got {0} {1} POSTing to "{2}"'.format(e.code, msg, path)
        )
        return {'success': False, 'result': e.code}


def post_request(opener, path, data):
    """Helper function for POSTing JSON data."""
    request = urllib.request.Request(path)
    request.add_header('Content-Type', 'application/json;charset=utf-8')
    def _post(request, data):
        with opener.open(request, json.dumps(data).encode()) as resp:
            return {
                'success': True,
                'result': json.loads(resp.read().decode('utf-8'))
            }
    return request_wrapper(_post(request, data))


def get_request(opener, path):
    """Helper function for GETing JSON data."""
    request = urllib.request.Request(path)
    def _get(request):
        with opener.open(request) as resp:
            return {
                'success': True,
                'result': json.loads(resp.read().decode('utf-8'))
            }
    return request_wrapper(_get(request))


def get_events(opener, path, full, last_id):
    parameters = []
    if full:
        parameters.append('full=true')
    if last_id is None:
        parameters.append('limit=1')
    else:
        parameters.append('after={0}'.format(last_id))
    if parameters:
        path += '?{0}'.format('&'.join(parameters))
    response = get_request(opener, path)
    if response['success'] and response['result']['events']:
        last_id = response['result']['events'][0]['id']
    else:
        last_id = last_id
    return {
        'success': response['success'],
        'result': response['result'],
        'lastId': last_id
    }


class ClientBase(object):
    """Base class for a cred client, implementing most functionality."""

    def __init__(self, hostname, apikey, device, location, subscribe, ignore_scheduler=False, custom_schedule_interval=30):
        # Authentication parameters
        self.session_key = None
        self.id = None
        self.scheduled = None
        self.ping_timeout = None
        # Cookies and a base request builder
        self.cookiejar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookiejar)
        )
        # API server hostname
        self.hostname = hostname
        # Client configuration details
        self.apikey = apikey
        self.device = device
        self.location = location
        self.subscribe = subscribe
        self.ignore_scheduler = ignore_scheduler
        self.custom_schedule_interval = custom_schedule_interval
        # Some state keeping, for new events, subscribed events and threads
        self.last_event_id = None
        self.last_subscribedevent_id = None
        self.is_pulling = False

    def authenticate(self):
        """Authenticate the client with the server."""
        path = '/'.join([self.hostname, 'auth'])
        data = {
            'apikey': self.apikey,
            'device': self.device,
            'location': self.location,
            'subscribe': self.subscribe
        }
        logging.info('Authenticating with server')
        response = post_request(self.opener, path, data)
        if response['success']:
            logging.info('Authentication successful')
            self.session_key = response['result']['sessionKey']
            self.id = response['result']['id']
            if response['result']['scheduled']['assigned']:
                self.scheduled = response['result']['scheduled']['slot']
            else:
                self.scheduled = False
            self.ping_timeout = response['result']['PINGTimeout']
            return response['result']
        return False

    def get_new_subscribedevents(self, full=True):
        """Get a list of new events that the client is subscribed to."""
        path = '/'.join([self.hostname, 'clients', str(self.id), 'subscribedevents'])
        response = get_events(self.opener, path, full, self.last_subscribedevent_id)
        self.last_subscribedevent_id = response['lastId']
        logging.info('Fetching list of new subscribed events')
        if response['success'] and response['result']['events']:
            return response['result']['events']
        return []

    def get_new_events(self, full=True):
        """Get a list of new events."""
        path = '/'.join([self.hostname, 'events'])
        response = get_events(self.opener, path, full, self.last_event_id)
        self.last_event_id = response['lastId']
        logging.info('Fetching list of new events')
        if response['success'] and response['result']['events']:
            return response['result']['events']
        return []

    def get_clients(self, full=True):
        """Get a list of active clients."""
        path = '/'.join([self.hostname, 'clients'])
        parameters = []
        if full:
            parameters.append('full=true')
        if parameters:
            path += '?{0}'.format('&'.join(parameters))
        response = get_request(self.opener, path)
        logging.info('Fetching list of active clients')
        if response['success'] and response['result']['clients']:
            return response['result']['clients']
        return []

    def start_pulling_subscribedevents(self):
        """
        Start a daemon thread, if one doesn't exist, that periodically pulls for
        subscribed events.

        """
        # Return if we are already polling for events
        if self.is_pulling:
            return False
        if self.ignore_scheduler or self.scheduled is None:
            schedule_interval = self.custom_schedule_interval
        else:
            schedule_interval = self.scheduled
        def pull(obj, schedule_interval):
            """Check for the events in a loop."""
            next_pull = time.time()
            while True:
                if time.time() >= next_pull:
                    logging.info('Pulling for new events in daemon thread')
                    next_pull = time.time() + schedule_interval
                    try:
                        events = obj.get_new_subscribedevents()
                        for event in events:
                            obj.handle_event(event)
                    except Exception as e:
                        pass
                time.sleep(0.5)
        # The thread is a daemon, because it doesn't matter if the program exits
        # in the middle of an operation.
        logging.info('Starting periodical pulling daemon thread')
        d = threading.Thread(
            name='EventPull',
            target=pull,
            args=(self,schedule_interval)
        )
        d.setDaemon(True)
        d.start()
        return d

    def submit_event(self, name, action, value):
        """POST an event to the server."""
        path = '/'.join([self.hostname, 'events'])
        data = {
            'event': {
                'name': name,
                'location': self.location,
                'action': action,
                'value': value
            }
        }
        response = post_request(self.opener, path, data)
        if response['success']:
            logging.info(
                'POSTed event with ID {0}'.format(response['result']['event']['id'])
            )
            return response['result']
        return False

    def handle_event(self, event):
        """Actions to take on an event."""
        raise NotImplementedError()
