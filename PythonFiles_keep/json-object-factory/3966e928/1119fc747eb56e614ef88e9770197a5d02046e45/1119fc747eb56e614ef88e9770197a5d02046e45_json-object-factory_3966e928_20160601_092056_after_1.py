

def test_encode_decode(json_factory, custom_objects, encode_decode_funcs):
    from conftest import check_objects_equal

    Base = custom_objects['classes']['Base']

    func_types, cls_types = encode_decode_funcs(Base)

    encoder = func_types['encoder']
    decoder = func_types['decoder']

    json_factory.Registry.register(encoder, mode='encode')
    json_factory.Registry.register(decoder, mode='decode')

    src_obj = custom_objects['instances']

    s = json_factory.dumps(src_obj)
    new_obj = json_factory.loads(s)
    check_objects_equal(src_obj, new_obj)

def test_instance_methods(json_factory, custom_objects, encode_decode_funcs):
    from conftest import check_objects_equal

    Base = custom_objects['classes']['Base']

    func_types, cls_types = encode_decode_funcs(Base)

    Encoder = cls_types['Encoder']
    Decoder = cls_types['Decoder']
    EncoderDecoder = cls_types['EncoderDecoder']

    encoder = Encoder()
    decoder = Decoder()
    encoder_decoder = EncoderDecoder()

    json_factory.Registry.register(encoder)
    json_factory.Registry.register(decoder)

    src_obj = custom_objects['instances']

    s = json_factory.dumps(src_obj)
    new_obj = json_factory.loads(s)
    check_objects_equal(src_obj, new_obj)

    json_factory.Registry.unregister(Encoder)
    assert len(json_factory.Registry.objects) == 2

    json_factory.Registry.unregister(encoder)
    json_factory.Registry.unregister(decoder)

    assert len(json_factory.Registry.objects) == 0

    json_factory.Registry.register(encoder_decoder)

    s = json_factory.dumps(src_obj)
    new_obj = json_factory.loads(s)
    check_objects_equal(src_obj, new_obj)
