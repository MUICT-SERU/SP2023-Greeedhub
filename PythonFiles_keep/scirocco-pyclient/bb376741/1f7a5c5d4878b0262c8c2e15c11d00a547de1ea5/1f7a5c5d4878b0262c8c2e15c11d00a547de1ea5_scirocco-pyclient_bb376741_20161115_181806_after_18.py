import copy
import unittest

from urllib3._collections import HTTPHeaderDict

from sciroccoclient.metadata import MetaData, MetaDataHydrator, MetaDataDescriptor, \
    MetaDataHTTPHeadersFilter


class MetaDataHydratorTest(unittest.TestCase):
    def setUp(self):
        self.metadata_http_descriptor = MetaDataDescriptor(MetaData())
        self.metadata_http_headers_filter = MetaDataHTTPHeadersFilter(self.metadata_http_descriptor)
        self.hydrator = MetaDataHydrator()

    def test_hydrate_from_headers_exists(self):
        self.assertTrue('hydrate_from_headers' in dir(self.hydrator))

    def test_hydrate_from_fields_exists(self):
        self.assertTrue('hydrate_from_fields' in dir(self.hydrator))

    def test_hydrate_from_headers_empty_headers_due_to_filtering(self):
        headers = HTTPHeaderDict()
        headers.add('asasd', 'sdfsdf')
        metadata = MetaData()
        metadata_original = copy.deepcopy(metadata)
        self.assertEqual(str(sorted(metadata_original.__dict__)),
                         str(sorted(self.hydrator.hydrate_from_headers(metadata, headers).__dict__)))

    def test_hydrate_return_object(self):
        headers = HTTPHeaderDict()
        headers.add('asasd', 'sdfsdf')
        self.assertIsInstance(self.hydrator.hydrate_from_headers(MetaData(), headers), MetaData)

    def test_hydrate_from_fields_return_object(self):
        fields = {
            "node_source": "af123",
            "to": "af123"
        }
        response = self.hydrator.hydrate_from_fields(MetaData(), fields)

        self.assertIsInstance(response, MetaData)

    def test_hydrate_from_headers_can_omit_not_mapped(self):
        headers = {
            self.metadata_http_descriptor.get_http_header_by_field_name('node_source'): "af123",
            self.metadata_http_descriptor._compose_http_header_from_field_name("toooo"): "af123"
        }
        response = self.hydrator.hydrate_from_headers(MetaData(), headers)
        self.assertFalse(hasattr(response, 'toooo'))

    def test_hydrate_from_fields_can_omit_not_mapped(self):
        fields = {
            'node_source': "af123",
            "toooo": "af123"
        }
        response = self.hydrator.hydrate_from_fields(MetaData(), fields)
        self.assertFalse(hasattr(response, 'toooo'))



class MetaDataHTTPHeadersFilterTest(unittest.TestCase):
    def setUp(self):

        self.metadata_http_descriptor = MetaDataDescriptor(MetaData())
        self.metadata_http_headers_filter = MetaDataHTTPHeadersFilter(self.metadata_http_descriptor)

    def test_filter_system_exists(self):
        self.assertTrue('filter_system' in dir(self.metadata_http_headers_filter))

    def test_filter_http_exists(self):
        self.assertTrue('filter_http' in dir(self.metadata_http_headers_filter))

    def test_filter_http_filtering(self):

        system_headers = self.metadata_http_descriptor.get_all_http_headers()
        headers = HTTPHeaderDict()
        for h in system_headers:
            headers.add(h, h.upper())

        headers.add('another', 'header')

        self.assertEqual(1, len(self.metadata_http_headers_filter.filter_http(headers)))

    def test_filter_system_filtering(self):

        system_headers = self.metadata_http_descriptor.get_all_http_headers()
        headers = HTTPHeaderDict()
        for h in system_headers:
            headers.add(h, h.upper())

        count_system = len(system_headers)
        headers.add('another', 'header')
        self.assertEqual(count_system, len(self.metadata_http_headers_filter.filter_system(headers)))

    def test_filter_http_return_type(self):
        headers = HTTPHeaderDict()
        headers.add('header', 'asda')
        self.assertIsInstance(self.metadata_http_headers_filter.filter_http(headers), HTTPHeaderDict)

    def test_filter_system_return_type(self):
        headers = HTTPHeaderDict()
        headers.add('header', 'asda')
        self.assertIsInstance(self.metadata_http_headers_filter.filter_system(headers), HTTPHeaderDict)


class MetaDataDescriptorTest(unittest.TestCase):
    def setUp(self):
        self.sys_dat_http_headers_descriptor = MetaDataDescriptor(MetaData())

    def test_attribute_http_system_headers_prefix_fixed_value(self):
        self.assertEqual('Scirocco', self.sys_dat_http_headers_descriptor.prefix)

    def test_attribute_http_system_headers_separator_fixed_value(self):
        self.assertEqual('-', self.sys_dat_http_headers_descriptor.separator)

    def test_get_all_http_headers_exists(self):
        self.assertTrue('get_all_http_headers' in dir(self.sys_dat_http_headers_descriptor))

    def test_compose_http_header_from_field_name_exists(self):
        self.assertTrue('_compose_http_header_from_field_name' in dir(self.sys_dat_http_headers_descriptor))

    def test_get_all_fields_exists(self):
        self.assertTrue('get_all_fields' in dir(self.sys_dat_http_headers_descriptor))

    def test_get_system_headers_by_field_name_exists(self):
        self.assertTrue('get_http_header_by_field_name' in dir(self.sys_dat_http_headers_descriptor))

    def test__compose_http_header(self):
        header = self.sys_dat_http_headers_descriptor._compose_http_header_from_field_name('test_prop_syS')
        prefix = self.sys_dat_http_headers_descriptor.prefix
        separator = self.sys_dat_http_headers_descriptor.separator
        self.assertEqual(header, ''.join([prefix, separator, 'Test', separator, 'Prop', separator, 'Sys']))

    def test_number_of_system_headers(self):
        self.assertEqual(13, len(self.sys_dat_http_headers_descriptor.get_all_http_headers()))

    def test_get_all_http_headers(self):
        headers = []
        for sh in MetaData().__dict__:
            if not sh.startswith('__'):
                headers.append(self.sys_dat_http_headers_descriptor._compose_http_header_from_field_name(sh))

        self.assertListEqual(headers, self.sys_dat_http_headers_descriptor.get_all_http_headers())

    def test_get_all_fields(self):
        fields = []
        for sh in MetaData().__dict__:
            if not sh.startswith('__'):
                fields.append(sh)
        self.assertListEqual(fields, self.sys_dat_http_headers_descriptor.get_all_fields())

    def test_get_http_header_by_field_name_raises_when_not_exists_in_metadata_entity(self):
        self.assertRaises(AttributeError, self.sys_dat_http_headers_descriptor.get_http_header_by_field_name,
                          'nonexistent')

    def test_get_http_header_by_field_name(self):
        prefix = self.sys_dat_http_headers_descriptor.prefix
        separator = self.sys_dat_http_headers_descriptor.separator
        expected_header = ''.join([prefix, separator, 'Update', separator, 'Time'])
        converted_header = self.sys_dat_http_headers_descriptor.get_http_header_by_field_name('update_time')
        self.assertEqual(expected_header, converted_header)


class MetaDataTest(unittest.TestCase):
    def setUp(self):
        self.sys_dat = MetaData()

    def test_attribute_node_destination_exist(self):
        self.assertTrue(hasattr(self.sys_dat, 'node_destination'))

    def test_attribute_node_source_exist(self):
        self.assertTrue(hasattr(self.sys_dat, 'node_source'))

    def test_attribute_id_exist(self):
        self.assertTrue(hasattr(self.sys_dat, 'id'))

    def test_attribute_topic_exist(self):
        self.assertTrue(hasattr(self.sys_dat, 'topic'))

    def test_attribute_status_exist(self):
        self.assertTrue(hasattr(self.sys_dat, 'status'))

    def test_attribute_update_time(self):
        self.assertTrue(hasattr(self.sys_dat, 'update_time'))

    def test_attribute_created_time(self):
        self.assertTrue(hasattr(self.sys_dat, 'created_time'))

    def test_attribute_scheduled_time(self):
        self.assertTrue(hasattr(self.sys_dat, 'scheduled_time'))

    def test_attribute_error_time(self):
        self.assertTrue(hasattr(self.sys_dat, 'error_time'))

    def test_attribute_processed_time(self):
        self.assertTrue(hasattr(self.sys_dat, 'processed_time'))

    def test_attribute_processing_time(self):
        self.assertTrue(hasattr(self.sys_dat, 'processing_time'))

    def test_attribute_tries(self):
        self.assertTrue(hasattr(self.sys_dat, 'tries'))

    def test_attribute_payload_type(self):
        self.assertTrue(hasattr(self.sys_dat, 'payload_type'))

    def test_setter_from_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.node_source = data
        self.assertEqual(data, self.sys_dat.node_source)

    def test_setter_to_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.node_destination = data
        self.assertEqual(data, self.sys_dat.node_destination)

    def test_setter_id_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.id = data
        self.assertEqual(data, self.sys_dat.id)

    def test_setter_topic_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.topic = data
        self.assertEqual(data, self.sys_dat.topic)

    def test_setter_status_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.status = data
        self.assertEqual(data, self.sys_dat.status)

    def test_setter_update_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.update_time = data
        self.assertEqual(data, self.sys_dat.update_time)

    def test_setter_created_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.created_time = data
        self.assertEqual(data, self.sys_dat.created_time)

    def test_setter_scheduled_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.scheduled_time = data
        self.assertEqual(data, self.sys_dat.scheduled_time)

    def test_setter_error_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.error = data
        self.assertEqual(data, self.sys_dat.error)

    def test_setter_processed_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.processed_time = data
        self.assertEqual(data, self.sys_dat.processed_time)

    def test_setter_processing_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.processing_time = data
        self.assertEqual(data, self.sys_dat.processing_time)

    def test_setter_tries_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.tries = data
        self.assertEqual(data, self.sys_dat.tries)

    def test_setter_data_type_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.payload_type = data
        self.assertEqual(data, self.sys_dat.payload_type)
