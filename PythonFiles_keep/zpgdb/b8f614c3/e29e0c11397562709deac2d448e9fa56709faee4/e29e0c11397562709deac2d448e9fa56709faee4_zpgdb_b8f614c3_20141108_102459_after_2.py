# -*- coding: utf-8 -*-

"""This module provides a thin wrapper to access a PostgreSQL database,
with functions to create a connection per thread, context managers to
wrap transactions, etc"""

import psycopg2
import psycopg2.extras
import psycopg2.extensions
import threading
from contextlib import contextmanager

HOST = PORT = DB = USER = PASS = None

_local = threading.local()

def getdb():
    "Return a database connection object. Reuse connections on same thread"
    if not hasattr(_local, 'dbh'):
        _local.dbh = psycopg2.connect(host=HOST, port=PORT,
            database=DB, user=USER, password=PASS,
            cursor_factory=psycopg2.extras.DictCursor)
    return _local.dbh

@contextmanager
def trans():
    open_trans = False
    dbh = getdb()
    if dbh.get_transaction_status() != psycopg2.extensions.TRANSACTION_STATUS_IDLE:
        open_trans = True
    c = dbh.cursor()
    try:
        yield c
    except:
        dbh.rollback()
        raise
    else:
        if not open_trans:
            dbh.commit()
    finally:
        c.close()

