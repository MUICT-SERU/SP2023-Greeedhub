import sqlite3

from flask import Flask, g

from flask_jsonschema_alt import FlaskJsonSchemaAlt, schema_json
from flask_jsonschema_alt.drivers import SqlAlchemyDriver

from models import Base, Post, Session, create_engine

app = Flask(__name__)
app.config.update(dict(
    DATABASE='sqlite:///:memory:',
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
jsonschema = FlaskJsonSchemaAlt(app, SqlAlchemyDriver)


@app.route('/', methods=['POST', 'PUT'])
@schema_json(Post)
def root():
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
