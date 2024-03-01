from flask import Flask, g

from flask_jsonschema_ext import FlaskJsonSchemaExt, schema_json
from flask_jsonschema_ext.drivers import SqlAlchemyDriver

from .models import Base, Post, Author, Session, create_engine

app = Flask(__name__)
app.config.update(dict(
    DATABASE='sqlite:///:memory:',
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
jsonschema = FlaskJsonSchemaExt(app, SqlAlchemyDriver)


@app.route('/post', methods=['POST', 'PUT'])
@schema_json(Post, {'__jsonschema_exclude__': ['post_id']})
def post_root():
    return ""


@app.route('/author', methods=['POST', 'PUT'])
@schema_json(Author, {'__jsonschema_include__': ['author_name'], 'posts': {'__jsonschema_include__': ['post_value']}})
def author_root():
    return ""


def init_db():
    Base.metadata.create_all(create_engine(app.config['DATABASE']))


def connect_db():
    """Connects to the specific database."""
    Session.configure(app.config['DATABASE'])
    return Session()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error=None):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.run()
