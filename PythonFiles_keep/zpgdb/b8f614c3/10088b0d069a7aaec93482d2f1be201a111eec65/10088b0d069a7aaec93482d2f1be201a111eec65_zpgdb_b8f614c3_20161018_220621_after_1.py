#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# To run these tests, first create a file named tests_config.py, with
# configurations pointing to a PostgreSQL database used for the tests
# (the database will be modified!), with this syntax:
# HOST = 127.0.0.1
# PORT = 5432
# USER = postgres
# PASS = postgres_password
# DB = SomeTestDatabase
#

import unittest
import psycopg2

import tests_config
import zpgdb as db

from uuid import uuid4

def rand():
    return 'tmp_' + str(uuid4()).replace('-', '')

class TestDb(unittest.TestCase):

    def test_getdb(self):
        "Make connection"
        dbh = db.getdb()
        self.assertFalse(dbh.closed)

    def test_getdb_reuse(self):
        "Test connection reuse on same thread"
        dbh1 = db.getdb()
        self.assertFalse(dbh1.closed)
        dbh2 = db.getdb()
        self.assertFalse(dbh2.closed)
        self.assertEqual(dbh1, dbh2)

    def test_trans(self):
        "Test transaction with commit"
        tbl = rand()
        with db.trans() as c:
            c.execute("create table " + tbl  + " (test text)")
            c.execute("insert into " + tbl + " values ('test')")
        with db.trans() as c:
            c.execute("select test from " + tbl + " limit 1")
            r = c.fetchone()
            self.assertEqual(r[0], 'test')

    def test_trans_rollback(self):
        "Test transaction with rollback"
        tbl = rand()
        with db.trans() as c:
            c.execute("create table " + tbl  + " (test text)")
        with self.assertRaises(psycopg2.DataError):
            with db.trans() as c:
                c.execute("insert into " + tbl + " values ('test')")
                c.execute("select 1/0")
        with db.trans() as c:
            c.execute("select test from " + tbl + " limit 1")
            r = c.fetchone()
            self.assertIs(r, None)


if __name__ == '__main__':
    db.config_connection(tests_config.HOST, tests_config.PORT,
        tests_config.USER, tests_config.PASS, tests_config.DB)
    unittest.main()
