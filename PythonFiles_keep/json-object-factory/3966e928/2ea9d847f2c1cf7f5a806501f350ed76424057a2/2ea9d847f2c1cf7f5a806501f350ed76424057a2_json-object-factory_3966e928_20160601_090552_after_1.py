import sys
import types
from functools import wraps

from jsonfactory.registry import FactoryWrapper, Registry, _build_wrapper

PY2 = sys.version_info.major == 2


def register(obj, mode=None):
    w = _build_wrapper(obj, mode)
    Registry.register(w)
    return obj

def encoder(obj):
    return register(obj, 'encode')

def decoder(obj):
    return register(obj, 'decode')
