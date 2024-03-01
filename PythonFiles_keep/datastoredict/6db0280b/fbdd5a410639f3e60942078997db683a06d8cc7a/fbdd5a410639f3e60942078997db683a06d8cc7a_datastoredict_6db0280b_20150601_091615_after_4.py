"""
A durabledict implementation for AppEngine
"""
import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'VERSION')) as f:
    __version__ = f.read().strip()

__all__ = ['DatastoreDict']

from datastoredict import DatastoreDict
