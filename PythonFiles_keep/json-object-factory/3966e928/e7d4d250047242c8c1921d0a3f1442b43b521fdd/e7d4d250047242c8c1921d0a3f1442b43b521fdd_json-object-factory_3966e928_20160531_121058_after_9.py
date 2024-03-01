import pytest

def check_objects_equal(src_obj, test_obj):
    assert set(src_obj.keys()) == set(test_obj.keys())
    for key, src_l in src_obj.items():
        assert len(test_obj[key]) == len(src_l)
        for i, obj in enumerate(src_l):
            assert obj == test_obj[key][i]

@pytest.fixture
def json_factory():
    import jsonfactory
    jsonfactory.Registry.objects.clear()
    return jsonfactory

@pytest.fixture
def custom_objects(request):
    class Base(object):
        def __init__(self, data):
            self.data = data
        @classmethod
        def find_subclass(cls, clsname):
            if clsname == cls.__name__:
                return cls
            for _cls in cls.__subclasses__():
                r = _cls.find_subclass(clsname)
                if r:
                    return r
        def __eq__(self, other):
            if other.__class__ != self.__class__:
                return False
            return other.data == self.data
        def __ne__(self, other):
            return not self.__eq__(other)
    class A(Base):
        pass
    class B(A):
        pass

    d = dict(
        classes={cls.__name__:cls for cls in (Base, A, B)},
        instances={},
    )
    for cls in (A, B):
        l = []
        for x in range(8):
            data = ['{}{}'.format(cls.__name__, y) for y in range(10)]
            obj = cls(data)
            l.append(obj)
        d['instances'][cls.__name__] = l

    return d

@pytest.fixture
def encode_decode_funcs():
    def build_funcs(Base):
        def encoder(o):
            if isinstance(o, Base):
                return {'_class_name_':o.__class__.__name__, 'data':o.data}
        def decoder(d):
            clsname = d.get('_class_name_')
            if clsname is not None:
                cls = Base.find_subclass(clsname)
                return cls(d['data'])
            return d
        class Encoder(object):
            def encode(self, o):
                return encoder(o)
        class Decoder(object):
            def decode(self, d):
                return decoder(d)
        class EncoderDecoder(Encoder, Decoder):
            pass
        func_types = dict(encoder=encoder, decoder=decoder)
        cls_types = {cls.__name__:cls for cls in (Encoder, Decoder, EncoderDecoder)}
        return func_types, cls_types
    return build_funcs
