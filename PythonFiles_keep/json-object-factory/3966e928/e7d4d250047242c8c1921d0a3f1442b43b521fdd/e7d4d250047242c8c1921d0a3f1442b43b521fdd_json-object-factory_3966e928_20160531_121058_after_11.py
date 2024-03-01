
def test_func_decorators(json_factory, custom_objects, encode_decode_funcs):
    from conftest import check_objects_equal

    Base = custom_objects['classes']['Base']

    func_types, cls_types = encode_decode_funcs(Base)

    @json_factory.decoder
    def decoder(d):
        return func_types['decoder'](d)

    @json_factory.encoder
    def encoder(o):
        return func_types['encoder'](o)

    src_obj = custom_objects['instances']

    s = json_factory.dumps(src_obj)
    new_obj = json_factory.loads(s)
    check_objects_equal(src_obj, new_obj)

def test_cls_decorators(json_factory, custom_objects, encode_decode_funcs):
    from conftest import check_objects_equal

    Base = custom_objects['classes']['Base']

    func_types, cls_types = encode_decode_funcs(Base)

    @json_factory.register
    class EncoderDecoder_(cls_types['EncoderDecoder']):
        pass

    src_obj = custom_objects['instances']

    s = json_factory.dumps(src_obj)
    new_obj = json_factory.loads(s)
    check_objects_equal(src_obj, new_obj)
