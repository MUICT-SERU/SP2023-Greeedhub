from unittest import TestCase
import random

import pyco_mongo
from pyco_mongo.errors import (
    MongoLocked,
    MongoNotFound,
    MongoKeyFrozen,
    MongoKeyUndefined,
    MongoFieldUnmovable,
)


class T_User(pyco_mongo.MongoMixin):
    __fields__ = [
        ('username', str, ''),
        ('email', str, ''),
        ('phone', str, ''),
    ]

    __frozen_keys__ = [
        'username',
    ]


t_col = T_User.__name__


class TestMongo(TestCase):
    def setUp(self):
        print('start test ...')

    def tearDown(self):
        print('tearDown, drop ')
        pyco_mongo._drop(t_col)

    def test_coll_cur_id(self):
        try:
            tid = pyco_mongo._coll_cur_id(t_col)
        except MongoNotFound as e:
            print(e.msg)
        else:
            assert isinstance(tid, int)
            print(tid)

    def test_next_id(self):
        tid = pyco_mongo._next_id(t_col)
        assert isinstance(tid, int)
        print(tid)

    def test_reset_id(self, id=0):
        tid = pyco_mongo._reset_id(t_col, id)
        print(tid)
        assert tid == 0

    def test_main(self):
        nid = 0
        self.test_reset_id(nid)
        self.test_coll_cur_id()
        self.test_next_id()
        cid = pyco_mongo._coll_cur_id(t_col)
        tid = pyco_mongo._next_id(t_col)
        assert tid == cid + 1
        pyco_mongo._reset_id(nid)


class TestMongoMinxin(TestCase):
    def setUp(self):
        print('start test ...')
        pyco_mongo._reset_id(t_col, 0)

    def tearDown(self):
        print('tearDown, drop {}'.format(t_col))
        pyco_mongo._drop(t_col)

    def test_new(self):
        uid = pyco_mongo._coll_cur_id(t_col) + 1
        uname = 'tn_{}'.format(uid)
        u = T_User.new(username=uname)
        ks = T_User.keys()
        assert uid == u.id
        assert u.username == uname
        assert u.keys() == ks
        assert '_type' in u.json()
        assert '_type' not in u.to_dict()

    def test_lock(self):
        u = T_User(username='loser')
        try:
            u.save()
        except MongoLocked as e:
            print(e.msg)
        else:
            print('locked failed ..')
            assert False

    def test_update(self):
        uname = 'upper'
        u = T_User.new(username=uname)
        try:
            u.update(username='loser')
        except MongoKeyFrozen as e:
            print(e.msg)
        else:
            print('froze failed ..')
            assert False
        email = 'xxxx@email.com'
        u.update(email=email)
        u2 = T_User.get(u.id)
        assert u2.email == u.email == email
        assert u2 == u

    def test_upsert(self):
        query = dict(
            username='user_xxx',
            email='user_xxx@email.com',
        )
        phone = str(random.randint(1000000, 10000000))
        update = dict(
            phone=phone
        )
        u1 = T_User.upsert(query, update)
        assert u1.username == 'user_xxx'
        assert u1.email == 'user_xxx@email.com'
        assert u1.phone == phone
        phone = str(random.randint(1000000, 10000000))
        update = dict(
            phone=phone,
        )
        u2 = T_User.upsert(query, update)
        assert u2.id == u1.id
        assert u2.phone == phone

    def test_add_field(self):
        try:
            T_User._add_field('password', '123456')
        except MongoKeyUndefined as e:
            print(e.msg)
            assert True
        else:
            assert False

    def test_del_field(self):
        try:
            T_User._del_field('email')
        except MongoFieldUnmovable as e:
            print(e.msg)
            assert True
        else:
            assert False

    def test_paging(self):
        for u in T_User.paging(limit=1):
            assert isinstance(u, T_User)

    def test_main(self):
        count = 3

        # test new
        u = T_User.new(username='tnx')
        for i in range(count - 1):
            uname = 'tnx_{}'.format(i)
            new_u = T_User.new(username=uname)
            assert u.id == new_u.id - 1
            u = new_u

        # test find_ond
        tu = T_User.find_one(id=u.id)
        assert tu == u

        # test find
        us = T_User.find()
        assert isinstance(us, list)
        assert len(us) == count
        assert T_User.count() == count
        assert u in us

        # test delete
        u.delete()
        assert u.deleted == True

        # test count
        ms = T_User.find(deleted=False)
        assert T_User.count(deleted=False) == len(ms)
        assert u not in ms

        # test recover
        u.recover()
        assert u.deleted == False

        # test paging
        ps = T_User.paging(limit=1)
        print(type(u))
        assert len(ps) == 1
        assert isinstance(ps[0], type(u))

    def test_filter_by_field_values(self):
        for i in range(20):
            v = 'user_{}'.format(i)
            T_User.new(username=v)
        c = 10
        vs = ['user_{}'.format(x) for x in range(c)]
        ms = T_User.find()
        ds = T_User.filter_by_field_values(ms, key='username', values=vs)
        dc = len(ds)
        assert (dc == c)

    def test_group_by_field_values(self):
        for i in range(20):
            v = 'user_{}'.format(i)
            T_User.new(username=v)
        c = 10
        vs = ['user_{}'.format(x) for x in range(c)]
        ms = T_User.find()
        ds = T_User.group_by_field_values(ms, key='username', values=vs)
        assert len(ds) == len(vs) == c
