#!/usr/bin/env python


from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bigtempo import DatastoreAPI


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

db = SQLAlchemy(app)
datastore = DatastoreAPI(app, db.engine)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
