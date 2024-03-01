from pyco_mongo import MongoMixin
import random
import hashlib


class User(MongoMixin):
    __fields__ = [
        ('username', str, ''),
        ('password', str, ''),
        ('email', str, ''),
        ('salt', str, ''),
    ]

    __frozen_keys__ = [
        'username',
    ]

    def __init__(self):
        super(User, self).__init__()
        self.salted_password()

    def salted_password(self):
        self.salt = str(random.randint(100000, 999999))
        hash1 = hashlib.md5(self.password.encode('ascii')).hexdigest()
        hash2 = hashlib.md5((hash1 + self.salt).encode('ascii')).hexdigest()
        self.password = hash2


class Todo(MongoMixin):
    __fields__ = [
        ('user_id', int, -1),
        ('title', str, ''),
        ('content', str, ''),
    ]

    def user(self):
        u = User.get(self.user_id)
        return u

    def uson(self):
        m = self.json()
        m['user'] = self.user().json()
        return m
