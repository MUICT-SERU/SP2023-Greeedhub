from __future__ import print_function

import copy
from collections import OrderedDict
from operator import itemgetter as _itemgetter

import six


class TypedNamedTupleMeta(type):
    def __new__(mcl, name, parents, dct):

        new_p = copy.copy(parents)

        fields = {}
        for k, v in dct.items():
            if k.startswith("_"):
                continue
            if type(v) is type:
                fields[k] = v
        new_d = {k: v for k, v in dct.items() if k not in fields}

        if name == "TypedNamedTuple":
            return super(TypedNamedTupleMeta,
                         mcl).__new__(mcl, name, parents, dct)

        if fields:
            field_names = tuple(sorted(fields.keys()))
            new_d["_fields"] = field_names
            types = {}
            for field_name, idx in zip(field_names, range(len(field_names))):
                new_d[field_name] = property(_itemgetter(idx),
                                             doc='Alias for field number %d' % idx)
                types[field_name] = fields[field_name]
            new_d["_types"] = types
        ret = super(TypedNamedTupleMeta,
                    mcl).__new__(mcl, name, tuple(new_p), new_d)
        return ret



@six.add_metaclass(TypedNamedTupleMeta)
class TypedNamedTuple(tuple):

    __slots__ = ()

    _fields = ()
    _types = {}
    def __new__(_cls, *args, **kw):
        """Create new instance of namedtype tuple."""
        typed_args = _cls._type_check(*args, **kw)
        return super(TypedNamedTuple, _cls).__new__(_cls, typed_args)

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new NT object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != len(cls._fields):
            raise TypeError('Expected %d arguments, got %d' % (
                len(cls._fields), len(result)))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        args = zip(self._fields, self)
        arg_strs = ["%s=%r" % pair for pair in args]
        return '%s(%s)' % (self.__class__.__name__,
                           ", ".join(arg_strs))

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new object replacing specified fields with new values'
        result = _self._make(map(kwds.pop, _self._fields, _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    __dict__ = property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        pass

    @classmethod
    def _type_check(cls, *args, **kw):
        """Check types of args against cls expected types.

        If the type is the expected type, pass though.
        If the type isn't then pass the argument through the type as callable
        to see if coercion is possible.
        """

        ret = []

        if len(args) > len(cls._fields):
            msg = ("__new__() takes %d positional arguments but %d were given"
                   % (len(cls._fields), len(args)))
            raise TypeError(msg)

        faz = zip(cls._fields, args)
        for field, arg in faz:
            typ = cls._types[field]
            if isinstance(arg, typ):
                ret.append(arg)
            else:
                ret.append(typ(arg))

        missing = []
        # Only look for fields not in arg list.
        for field in cls._fields[len(ret):]:
            if field in kw:
                typ = cls._types[field]
                arg = kw[field]
                if isinstance(arg, typ):
                    ret.append(arg)
                else:
                    ret.append(typ(arg))
            else:
                missing.append(field)
        if missing:
            raise TypeError("%s missing %d required positional argument%s: %s"
                            % (cls.__name__, len(missing), 
                               "s" if len(missing)>1 else "",
                               ", ".join([repr(m) for m in missing])))
                           
        return ret

    def to_dict(self):
        return dict(zip(self._fields, tuple(self)))
