# -*- coding: utf-8 -*-

import json

from flask import Flask, Response

from flask_filtered_response import filtered

app = Flask('flask-test-response')


@app.route('/filtered/single_node')
@filtered
def single_node():
    response_dict = {
        'test_int': 123,
        'test_string': 'Hey!',
    }
    return Response(json.dumps(response_dict))


@app.route('/filtered/multiple_nodes')
@filtered
def multiple_nodes():
    response_list = [
        {
            'test_int': 123,
            'test_string': 'Hey!',
        },
        {
            'test_int': 456,
            'test_string': 'Yo!',
        },
    ]
    return Response(json.dumps(response_list))
