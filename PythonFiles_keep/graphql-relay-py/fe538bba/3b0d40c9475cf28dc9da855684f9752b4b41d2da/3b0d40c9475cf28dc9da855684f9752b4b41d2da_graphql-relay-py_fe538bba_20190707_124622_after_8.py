import base64

from graphql_relay.utils.base64 import base64, unbase64


example_unicode = 'Some examples: ❤😀'
example_base64 = 'U29tZSBleGFtcGxlczog4p2k8J+YgA=='


def test_converts_from_unicode_to_base64():
    assert base64(example_unicode) == example_base64


def test_converts_from_base_64_to_unicode():
    assert unbase64(example_base64) == example_unicode
