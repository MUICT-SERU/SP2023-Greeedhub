#!/usr/bin/env python

""" Improved implementation of netrc spec as a JSON file, allow for arbitrary key, value pairs.

    Example netrc.json:
    {
        "smtp" : {
            "host": "mail.example.com",
            "port": 587,
            "username": "alice@example.com",
            "password": "password",
            "from": "alice@example.com",
            "to": "bob@example.com"
        }
    }

"""
import json
import os
import stat


class AttrDict(dict):
    """ Attribute access dictionary.
        https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class Netrc(AttrDict):
    """ Attribute proxy to netrc.json file.
    """
    def __init__(self, path='~/netrc.json', section=None):
        path = os.path.expanduser(path)
        if os.path.exists(path):
            netrc = json.load(open(path, 'r'))
        else:
            netrc = {}
        super().__init__(netrc.get(section, {}))

        self.__path = path
        self.__section = section
        self.__netrc = netrc

    def save(self):
        """ Save the changes.
        """
        d = self.__dict__.copy()
        for key in list(d):
            if key.startswith('_Netrc'):
                d.pop(key, None)

        with open(self.__path, 'w') as f:
            self.__netrc[self.__section] = d
            json.dump(self.__netrc, f, indent=4)

        os.chmod(self.__path, stat.S_IRUSR | stat.S_IWUSR)
