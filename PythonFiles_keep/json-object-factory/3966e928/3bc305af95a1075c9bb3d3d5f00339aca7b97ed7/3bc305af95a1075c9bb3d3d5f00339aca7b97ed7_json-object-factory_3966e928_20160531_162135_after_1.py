import sys
import types
from functools import wraps

from jsonfactory.registry import FactoryWrapper, Registry

PY2 = sys.version_info.major == 2

def _decorate(obj, mode):
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
    elif isinstance(obj, types.MethodType):
        if PY2:
            cls = obj.im_class
            inst = obj.im_self
        else:
            inst = obj.__self__
            cls = inst.__class__
        f = obj
        if inst is None:
            inst = cls()
        @wraps(f)
        def wrapper(*args):
            return f(inst, *args)
        if mode == 'encode':
            w = FactoryWrapper(inst, mode=mode, encode_func=wrapper)
        elif mode == 'decode':
            w = FactoryWrapper(inst, mode=mode, decode_func=wrapper)
        else:
            w = FactoryWrapper(wrapper, mode=mode)
    Registry.register(w)
    if wrapper is None:
        wrapper = obj
    return obj

def register(obj, mode=None):
    r = _decorate(obj, mode)
    return r

def encoder(obj):
    return _decorate(obj, 'encode')

def decoder(obj):
    return _decorate(obj, 'decode')
