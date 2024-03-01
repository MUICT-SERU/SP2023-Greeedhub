import sys
import types
from functools import wraps

from jsonfactory.registry import FactoryWrapper, Registry

PY2 = sys.version_info.major == 2

def _build_wrapper(obj, mode):
    inst = None
    if isinstance(obj, types.FunctionType):
        f = obj
        wrapper = None
        w = FactoryWrapper(f, mode=mode)
    elif isinstance(obj, type):
        inst = obj()
        wrapper = None
        w = FactoryWrapper(inst, mode=mode, obj_id=id(obj))
    elif isinstance(obj.__class__, type):
        inst = obj
        wrapper = None
        w = FactoryWrapper(obj, mode=mode)
    return w

def register(obj, mode=None):
    w = _build_wrapper(obj, mode)
    Registry.register(w)
    return obj

def encoder(obj):
    return register(obj, 'encode')

def decoder(obj):
    return register(obj, 'decode')
