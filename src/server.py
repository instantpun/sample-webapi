### Standard Libs
import sys
import random
import time
import hashlib
import json
from datetime import date

### 3rd Party Libs
import fastapi
import requests
from prometheus_client import make_wsgi_app, start_http_server, Summary, Counter, Gauge
 

### Prometheus metrics ###
# pattern:

REQUEST_TIME = Summary('request_processing_seconds','Time spent processing request') # TODO: add labels somehow
REQUEST_COUNT = Counter('request_count', 'Total number of requests processed by endpoint', ('method','context','uri_path'))
REQUEST_RUNNING = Gauge('request_running', 'Number of requests currently being processed', ('method','context','uri_path'))
SESSION_OBJECTS = Gauge('session_count', 'Total number of known ids', ('method','context','uri_path'))

# sample user data
session_data = {
    "256d56db73189f8c9c803dbfde9624c19f35d1fdd3aed0765f8d33f19f1a22f7b79": {
        "first_name": 'aaron',
        "last_name": 'robinett',
        "session_expiry": '2021-11-19T16:59:30.685144',
        "login_successful": True
    }
}

# track growth of session data object by configuring callback for Gauge Metric
SESSION_OBJECTS.set_function(lambda: len(session_data))


@REQUEST_TIME.time()
def get_session_by_id(id):
    """
    """
    get_session_by_id_labels = dict(
        method='get',
        context='get_session_by_id',
        uri_path='/api/v1/session'
    )
    REQUEST_COUNT.labels(**get_session_by_id_labels).inc()
    with REQUEST_RUNNING.labels(**get_session_by_id_labels).track_progress():

        result = session_data.get(id)

        if not result:
            resp_code = 404
            return {'error':'Not Found'}, resp_code, {'Content-Type':'application/json'}
        else:
            resp_code = 200
            return {id: result}, resp_code, {'Content-Type':'application/json'}

def create_session():
    """
    """

    create_session_labels = dict(
        method='post',
        context='create_session',
        uri_path='/api/v1/session/create'
    )
    REQUEST_COUNT.labels(**create_session_labels).inc()
    with REQUEST_RUNNING.labels(**create_session_labels).track_progress():
        session = None

        try:
            session = $$request.data
            session = json.loads(session)
        except TypeError as e:
            print("ERROR: request data is None")
        except json.decoder.JSONDecodeError as e:
            print("ERROR: json decoding failed")
        
        if not session:
            return {'error':'Not Found'}, 404, {'Content-Type':'application/json'}
        
        session_id = None

        # combine inputs into byte string, and generate sha256 hash as the id:
        inputs = [session['first_name'], session['last_name'], session['expiry']]
        hashable = ''.join(inputs)
        session_id = hashlib.sha3_256(hashable.encode('utf-8')).hexdigest()

        # update session_data cache
        session_data.update({session_id: session})

        return {'id': session_id}, 200, {'Content-Type':'application/json'}