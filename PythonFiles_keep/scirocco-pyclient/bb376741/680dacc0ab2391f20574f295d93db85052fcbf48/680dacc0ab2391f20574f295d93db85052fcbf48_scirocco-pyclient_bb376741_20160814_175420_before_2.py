import json


class Base:
    def parse_input(self, data):
        # TODO build object response bettter ??
        parsed_data = dict()
        parsed_data['headers'] = data.headers
        parsed_data['data'] = json.loads(data.data.decode("utf8"))
        parsed_data['system_data'] = {}

        for k, v in parsed_data['data'].items():

            if k != 'data':
                parsed_data['system_data'][k] = v

        return parsed_data
