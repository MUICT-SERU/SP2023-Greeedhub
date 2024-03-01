from .td import StreamingUploader

import gzip
import msgpack
import StringIO
import numpy as np
import pandas as pd

from unittest import TestCase
from nose.tools import eq_, raises

class TestClient(object):
    pass

class StreamingUploaderTestCase(TestCase):
    def setUp(self):
        client = TestClient()
        self.uploader = StreamingUploader(client, 'test_db', 'test_tbl')

    def test_normalize_time_now(self):
        frame = pd.DataFrame([['a', 1], ['b', 2]], columns=['x', 'y'])
        # default (= now)
        f1 = self.uploader.normalize_frame(frame)
        eq_(list(f1.columns), ['x', 'y', 'time'])
        # time='now'
        f2 = self.uploader.normalize_frame(frame, time='now')
        eq_(list(f2.columns), ['x', 'y', 'time'])

    def test_normalize_time_column(self):
        frame = pd.DataFrame([[0, 'a', 1], [0, 'b', 2]], columns=['time', 'x', 'y'])
        # time='column'
        f1 = self.uploader.normalize_frame(frame, time='column')
        eq_(list(f1.columns), ['time', 'x', 'y'])

    def test_normalize_time_index(self):
        date_range = pd.date_range('2015-01-01', periods=2, freq='d')
        frame = pd.DataFrame([['a', 1], ['b', 2]], columns=['x', 'y'], index=date_range)
        # time='index'
        f1 = self.uploader.normalize_frame(frame, time='index')
        eq_(list(f1.columns), ['x', 'y', 'time'])

    @raises(ValueError)
    def test_raise_invalid_time(self):
        frame = pd.DataFrame([['a', 1], ['b', 2]], columns=['x', 'y'])
        self.uploader.normalize_frame(frame, time='invalid')

    def test_chunk_frame(self):
        frame = pd.DataFrame([['a', 1], ['b', 2]], columns=['x', 'y'])
        for records in self.uploader.chunk_frame(frame):
            eq_(records, [{'x': 'a', 'y': 1}, {'x': 'b', 'y': 2}])

    def test_pack_gz(self):
        records = [{'x': 'a', 'y': 1}, {'x': 'b', 'y': 2}]
        data = self.uploader.pack_gz(records)
        with gzip.GzipFile(fileobj=StringIO.StringIO(data)) as f:
            for unpacked in msgpack.Unpacker(f):
                eq_(unpacked, records[0])
                records = records[1:]
        eq_(records, [])
