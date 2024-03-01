# -*- coding: utf-8 -*-

import json
from functools import wraps

from flask import request


def filtered(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        if request.method == 'GET':
            if 'fields' in request.args:
                required_fields = request.args.get('fields').split(',')
                response_obj = json.loads(response.data)

                if isinstance(response_obj, list):
                    filtered_data = __get_filtered_data_for_list(response_obj, required_fields)
                else:
                    filtered_data = __get_filtered_data_for_dict(response_obj, required_fields)
                response.data = json.dumps(filtered_data)
        return response
    return decorated


def __get_filtered_data_for_list(response_obj, required_fields):
    filtered_data = list()
    for node in response_obj:
        filtered_node = __get_filtered_data_for_dict(node, required_fields)
        filtered_data.append(filtered_node)
    return filtered_data


def __get_filtered_data_for_dict(response_obj, required_fields):
    keys = response_obj.keys()
    for key in keys:
        if key not in required_fields:
            response_obj.pop(key, None)
    return response_obj
