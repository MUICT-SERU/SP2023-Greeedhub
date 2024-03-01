import unittest

from pyddsclient.clientresponse import DataTypeConverter


class DataTypeConverterTest(unittest.TestCase):

    def setUp(self):
        self.converter = DataTypeConverter()

    def test_data_converter(self):

        str = '{"field1": "value1", "field2": "value2"}'
        btes = '{"field1": "value1", "field2": "value2"}'.encode("utf8")
        data_object = {"field1": "value1", "field2": "value2"}

        res1 = self.converter.convert_to_dict(str)
        res2 = self.converter.convert_to_dict(btes)
        res3 = self.converter.convert_to_dict(data_object)

        for r in [res1, res2, res3]:

            self.assertIsInstance(r, dict)