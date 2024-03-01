from flask import Flask, g

from flask_jsonschema_ext import FlaskJsonSchemaExt, jsonschema_generate
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
@jsonschema_generate(Post)
def post_root():
    return ""


@app.route('/author', methods=['POST', 'PUT'])
@jsonschema_generate(Author)
def author_root():
    return ""


def init_db():
    engine = create_engine(app.config['DATABASE'])
    Base.metadata.create_all(engine)
    return engine


def connect_db(engine=None):
    """Connects to the specific database."""
    engine = init_db()
    Session.configure(bind=engine)
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
