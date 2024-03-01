#!/usr/bin/env python


from flask import Flask
from flask.ext.bigtempo import BigTempoAPI


app = Flask(__name__)
bigtempo = BigTempoAPI(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
