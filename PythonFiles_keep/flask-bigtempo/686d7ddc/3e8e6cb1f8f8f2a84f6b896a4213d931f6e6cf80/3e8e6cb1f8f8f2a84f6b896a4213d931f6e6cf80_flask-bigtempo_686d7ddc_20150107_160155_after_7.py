import flask


def bigtempo_blueprint():
    blueprint = flask.Blueprint('bigtempo', __name__, template_folder='templates')

    @blueprint.route('/test')
    def index():
        return 'ok'

    return blueprint
