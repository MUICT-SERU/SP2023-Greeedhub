import flask
import pandas


_DEFAULT_JSON_FORMAT = 'columns'


def new_blueprint(storage, default_json_format=_DEFAULT_JSON_FORMAT):
    blueprint = flask.Blueprint('datastore', __name__, url_prefix='/api/store')


    @blueprint.route('/<reference>/<symbol>', methods=['POST', 'PUT'])
    def save(reference, symbol):
        jsonformat = flask.request.args.get('jsonformat', default_json_format)

        json = flask.request.get_data()
        data = pandas.read_json(json, orient=jsonformat)
        storage.save(data, reference, symbol)

        return flask.Response('', content_type='application/json')


    @blueprint.route('/<reference>/<symbol>', methods=['GET'])
    def retrieve(reference, symbol):
        jsonformat = flask.request.args.get('jsonformat', default_json_format)

        data = storage.retrieve(reference, symbol)
        if data is None:
            flask.abort(404)

        json = data.to_json(orient=jsonformat, date_format='iso')
        return flask.Response(json, content_type='application/json')


    return blueprint