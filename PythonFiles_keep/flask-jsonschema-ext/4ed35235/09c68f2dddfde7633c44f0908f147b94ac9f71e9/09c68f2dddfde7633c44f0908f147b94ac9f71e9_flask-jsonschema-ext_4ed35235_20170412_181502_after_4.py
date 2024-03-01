from flask import Flask, g, request, jsonify
from flask_jsonschema_ext import FlaskJsonSchemaExt, jsonschema_generate
from flask_jsonschema_ext.drivers import SqlAlchemyDriver

from colanderalchemy import SQLAlchemySchemaNode

from .models import Base, Post, Author, Session, create_engine

app = Flask(__name__)
app.config.update(dict(
    DATABASE='sqlite:///:memory:',
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
jsonschema = FlaskJsonSchemaExt(app, SqlAlchemyDriver)

row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}


@app.route('/post', methods=['POST', 'PUT'])
@jsonschema_generate(Post)
def post_root():
    session = get_db()
    schema = SQLAlchemySchemaNode(Post)
    post = schema.objectify(request.get_json())
    session.add(post)
    session.commit()
    return str(post.post_id)


@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    session = get_db()
    post = session.query(Post).get(post_id)
    return jsonify(row2dict(post))


@app.route('/author', methods=['POST', 'PUT'])
@jsonschema_generate(Author)
def author_root():
    session = get_db()
    schema = SQLAlchemySchemaNode(Author)
    author = schema.objectify(request.get_json())
    session.add(author)
    session.commit()
    return str(author.author_id)


@app.route('/author/<int:author_id>', methods=['GET'])
def get_author(author_id):
    session = get_db()
    author = session.query(Author).get(author_id)
    return jsonify(row2dict(author))


def init_db():
    engine = create_engine(app.config['DATABASE'])
    Base.metadata.create_all(engine)
    return engine


def connect_db():
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
