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

import tests_config
import zpgdb as db

db.HOST = tests_config.HOST
db.PORT = tests_config.PORT
db.USER = tests_config.USER
db.PASS = tests_config.PASS
db.DB = tests_config.DB


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
        self.assertEquals(dbh1, dbh2)



if __name__ == '__main__':
    unittest.main()
