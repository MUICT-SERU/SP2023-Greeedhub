#!/usr/bin/env python


from flask import Flask
from flask.ext.bigtempo import BigtempoAPI


# SETTING BIGTEMPO UP
import bigtempo.core

bigtempo_engine = bigtempo.core.DatasourceEngine()


## Creating sample datasources ################################################
import numpy
import pandas
from datetime import datetime as dt


@bigtempo_engine.datasource('SAMPLE')
class SampleDatasource(object):

    def evaluate(self, context, symbol, start=None, end=None):
        if start is None:
            start = dt(2000, 1, 1)

        if end is None:
            end = dt(2005, 1, 1)

        rng = pandas.date_range(start, end)
        data = numpy.random.randn(len(rng))
        return pandas.DataFrame(data, index=rng, columns=[symbol])
###############################################################################


# SETTING THE APP UP
app = Flask(__name__)
bigtempo_web = BigtempoAPI(app, bigtempo_engine)


@app.route('/')
def hello_world():
    return '''
           <h1>Welcome to the bigtempo web API example!</h1>
           Try accessing /api/bigtempo/{reference}/{symbol}<br />
           (eg.: /api/bigtempo/SAMPLE/blabla)
           '''


if __name__ == '__main__':
    app.run(debug=True)
