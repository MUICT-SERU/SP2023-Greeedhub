"""tests/test_validate.py.

Tests to ensure izi's custom validation methods work as expected

Copyright (C) 2016 Timothy Edmund Crosley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
import izi

TEST_SCHEMA = {'first': 'Timothy', 'place': 'Seattle'}


def test_all():
    """Test to ensure izi's all validation function works as expected to combine validators"""
    assert not izi.validate.all(izi.validate.contains_one_of('first', 'year'),
                                izi.validate.contains_one_of('last', 'place'))(TEST_SCHEMA)
    assert izi.validate.all(izi.validate.contains_one_of('last', 'year'),
                            izi.validate.contains_one_of('first', 'place'))(TEST_SCHEMA)


def test_any():
    """Test to ensure izi's any validation function works as expected to combine validators"""
    assert not izi.validate.any(izi.validate.contains_one_of('last', 'year'),
                                izi.validate.contains_one_of('first', 'place'))(TEST_SCHEMA)
    assert izi.validate.any(izi.validate.contains_one_of('last', 'year'),
                            izi.validate.contains_one_of('no', 'way'))(TEST_SCHEMA)


def test_contains_one_of():
    """Test to ensure izi's contains_one_of validation function works as expected to ensure presence of a field"""
    assert izi.validate.contains_one_of('no', 'way')(TEST_SCHEMA)
    assert not izi.validate.contains_one_of('last', 'place')(TEST_SCHEMA)
