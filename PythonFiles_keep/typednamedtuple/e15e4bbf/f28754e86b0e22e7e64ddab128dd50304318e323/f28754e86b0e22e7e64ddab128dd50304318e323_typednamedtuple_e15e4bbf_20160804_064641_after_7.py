from __future__ import print_function

from collections import namedtuple


class TypedNamedTupleMeta(type):
    def __new__(cls, name, parents, dct):
        # print("C:", cls)
        # print("N:", name)
        print("P:", parents)
        # print("D:", dct)

        new_p = []
        for p in parents:
            print("Pi:", p)
            print("Pd:", dir(p))
            print("Pn:", p.__name__)
            new_p.append(p)


        fields = {}
        for k, v in dct.items():
            if k.startswith("_"):
                continue
            if type(v) is type:
                print("Kt:", k, v)
                fields[k] = v
            else:
                print("Kp:", k)

        if fields:
            print("Have fields, make nt")
            t = namedtuple(name + "Base", fields.keys())
            new_p = [t] + new_p

        print("NP:", new_p)
        new_d = {k: v for k, v in dct.items() if k not in fields}
        return super(TypedNamedTupleMeta, cls).__new__(cls, name, tuple(new_p), new_d)

class TypedNamedTuple(object):
    __metaclass__ = TypedNamedTupleMeta

    def to_dict(self):
        return dict(self._asdict())
