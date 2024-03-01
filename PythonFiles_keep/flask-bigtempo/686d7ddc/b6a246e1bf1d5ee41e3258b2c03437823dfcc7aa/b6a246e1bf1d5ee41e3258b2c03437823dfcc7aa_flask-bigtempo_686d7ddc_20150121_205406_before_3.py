#!/usr/bin/env python
# -*- coding: utf-8 -*-


import flask
import pandas
import sqlalchemy

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from .blueprints.datastore import new_blueprint


_metadata = sqlalchemy.MetaData()


class DatastoreAPI(object):

    def __init__(self, app=None, sqlengine=None):
        self._storage = None

        self.app = app
        self.sqlengine = sqlengine

        if app is not None and sqlengine is not None:
            self.init_app(app, sqlengine)

    def init_app(self, app, sqlengine):
        app.register_blueprint(new_blueprint(self.instance))

    def _lazyload_instance(self):
        if self._storage is None:
            self._storage = SQLAlchemyStorage(self.sqlengine, '{reference}__{symbol}')
        return self._storage

    @property
    def instance(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'bigtempo_datastore_instance'):
                ctx.bigtempo_datastore_instance = self._lazyload_instance()
            return ctx.bigtempo_datastore_instance
        else:
            return self._lazyload_instance()


class SQLAlchemyStorage(object):

    def __init__(self, sqlengine, tablename_base='{reference}__{symbol}'):
        self.sqlengine = sqlengine
        self.tablename_base = tablename_base

    def save(self, dataframe, reference, symbol):
        tablename = self._tablename(reference, symbol)

        exists_table = self.sqlengine.has_table(tablename)
        if exists_table:
            start = _format_datetime(dataframe.index.values[0])
            end = _format_datetime(dataframe.index.values[-1], milis='0001')
            self.sqlengine.execute('DELETE FROM %s WHERE "index" >= "%s" AND "index" <= "%s"' % (tablename, start, end))

        dataframe.to_sql(tablename, self.sqlengine, if_exists='append')

        if not exists_table:
            table = sqlalchemy.Table(tablename, _metadata, autoload=True, autoload_with=self.sqlengine)
            sqlalchemy.Index('idx_index', table.c.index).create(self.sqlengine)

    def retrieve(self, reference, symbol):
        tablename = self._tablename(reference, symbol)

        exists_table = self.sqlengine.has_table(tablename)
        if not exists_table:
            return None

        return pandas.read_sql_query('SELECT * FROM "%s" ORDER BY "index"' % tablename, self.sqlengine, parse_dates=['index'], index_col='index')

    def _tablename(self, reference, symbol):
        return self.tablename_base.format(reference=reference, symbol=symbol)


def _format_datetime(datetime64, milis='0'):
    return pandas.to_datetime(str(datetime64)).strftime('%Y-%m-%d %H:%M:%S.' + milis)