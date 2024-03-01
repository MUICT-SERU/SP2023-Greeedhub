import copy
import unittest

from urllib3._collections import HTTPHeaderDict

from sciroccoclient.systemdata import SystemData, SystemDataHydrator, SystemDataDescriptor, \
    SystemDataHTTPHeadersFilter


class SystemDataHydratorTest(unittest.TestCase):
    def setUp(self):
        self.system_data_http_descriptor = SystemDataDescriptor(SystemData())
        self.system_data_http_headers_filter = SystemDataHTTPHeadersFilter(self.system_data_http_descriptor)
        self.hydrator = SystemDataHydrator()

    def test_hydrate_from_headers_exists(self):
        self.assertTrue('hydrate_from_headers' in dir(self.hydrator))

    def test_hydrate_from_fields_exists(self):
        self.assertTrue('hydrate_from_fields' in dir(self.hydrator))

    def test_perform_nomenclature_adjustments_exists(self):
        self.assertTrue('perform_nomenclature_adjustments' in dir(self.hydrator))

    def test_hydrate_from_headers_empty_headers_due_to_filtering(self):
        headers = HTTPHeaderDict()
        headers.add('asasd', 'sdfsdf')
        system_data = SystemData()
        system_data_original = copy.deepcopy(system_data)
        self.assertEqual(str(sorted(system_data_original.__dict__)),
                         str(sorted(self.hydrator.hydrate_from_headers(system_data, headers).__dict__)))

    def test_hydrate_return_object(self):
        headers = HTTPHeaderDict()
        headers.add('asasd', 'sdfsdf')
        self.assertIsInstance(self.hydrator.hydrate_from_headers(SystemData(), headers), SystemData)

    def test_hydrate_from_fields_return_object(self):
        fields = {
            "fromm": "af123",
            "to": "af123"
        }
        response = self.hydrator.hydrate_from_fields(SystemData(), fields)

        self.assertIsInstance(response, SystemData)

    def test_hydrate_from_headers_can_omit_not_mapped(self):
        headers = {
            self.system_data_http_descriptor.get_http_header_by_field_name('fromm'): "af123",
            self.system_data_http_descriptor._compose_http_header_from_field_name("toooo"): "af123"
        }
        response = self.hydrator.hydrate_from_headers(SystemData(), headers)
        self.assertFalse(hasattr(response, 'toooo'))

    def test_hydrate_from_fields_can_omit_not_mapped(self):
        fields = {
            "fromm": "af123",
            "toooo": "af123"
        }
        response = self.hydrator.hydrate_from_fields(SystemData(), fields)
        self.assertFalse(hasattr(response, 'toooo'))

    def test_perform_nomenclature_adjustments(self):
        name = 'from'
        result = self.hydrator.perform_nomenclature_adjustments(name)
        self.assertEqual(result, 'fromm')


class SystemDataHTTPHeadersFilterTest(unittest.TestCase):
    def setUp(self):

        self.system_data_http_descriptor = SystemDataDescriptor(SystemData())
        self.system_data_http_headers_filter = SystemDataHTTPHeadersFilter(self.system_data_http_descriptor)

    def test_filter_system_exists(self):
        self.assertTrue('filter_system' in dir(self.system_data_http_headers_filter))

    def test_filter_http_exists(self):
        self.assertTrue('filter_http' in dir(self.system_data_http_headers_filter))

    def test_filter_http_filtering(self):

        system_headers = self.system_data_http_descriptor.get_all_http_headers()
        headers = HTTPHeaderDict()
        for h in system_headers:
            headers.add(h, h.upper())

        headers.add('another', 'header')

        self.assertEquals(1, len(self.system_data_http_headers_filter.filter_http(headers)))

    def test_filter_system_filtering(self):

        system_headers = self.system_data_http_descriptor.get_all_http_headers()
        headers = HTTPHeaderDict()
        for h in system_headers:
            headers.add(h, h.upper())

        count_system = len(system_headers)
        headers.add('another', 'header')
        self.assertEquals(count_system, len(self.system_data_http_headers_filter.filter_system(headers)))

    def test_filter_http_return_type(self):
        headers = HTTPHeaderDict()
        headers.add('header', 'asda')
        self.assertIsInstance(self.system_data_http_headers_filter.filter_http(headers), HTTPHeaderDict)

    def test_filter_system_return_type(self):
        headers = HTTPHeaderDict()
        headers.add('header', 'asda')
        self.assertIsInstance(self.system_data_http_headers_filter.filter_system(headers), HTTPHeaderDict)


class SystemDataDescriptorTest(unittest.TestCase):
    def setUp(self):
        self.sys_dat_http_headers_descriptor = SystemDataDescriptor(SystemData())

    def test_attribute_http_system_headers_prefix_fixed_value(self):
        self.assertEquals('Scirocco', self.sys_dat_http_headers_descriptor.prefix)

    def test_attribute_http_system_headers_separator_fixed_value(self):
        self.assertEquals('-', self.sys_dat_http_headers_descriptor.separator)

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
        self.assertEquals(header, ''.join([prefix, separator, 'Test', separator, 'Prop', separator, 'Sys']))

    def test_header__compose_fromm_behaviour(self):
        header = self.sys_dat_http_headers_descriptor._compose_http_header_from_field_name('_fromm')
        prefix = self.sys_dat_http_headers_descriptor.prefix
        separator = self.sys_dat_http_headers_descriptor.separator
        self.assertEquals(header, ''.join([prefix, separator, 'From']))

    def test_number_of_system_headers(self):
        self.assertEqual(13, len(self.sys_dat_http_headers_descriptor.get_all_http_headers()))

    def test_get_all_http_headers(self):
        headers = []
        for sh in SystemData().__dict__:
            if not sh.startswith('__'):
                headers.append(self.sys_dat_http_headers_descriptor._compose_http_header_from_field_name(sh))

        self.assertListEqual(headers, self.sys_dat_http_headers_descriptor.get_all_http_headers())

    def test_get_all_fields(self):
        fields = []
        for sh in SystemData().__dict__:
            if not sh.startswith('__'):
                fields.append(sh)
        self.assertListEqual(fields, self.sys_dat_http_headers_descriptor.get_all_fields())

    def test_get_http_header_by_field_name_raises_when_not_exists_in_system_data_entity(self):
        self.assertRaises(AttributeError, self.sys_dat_http_headers_descriptor.get_http_header_by_field_name,
                          'nonexistent')

    def test_get_http_header_by_field_name(self):
        prefix = self.sys_dat_http_headers_descriptor.prefix
        separator = self.sys_dat_http_headers_descriptor.separator
        expected_header = ''.join([prefix, separator, 'Update', separator, 'Time'])
        converted_header = self.sys_dat_http_headers_descriptor.get_http_header_by_field_name('update_time')
        self.assertEqual(expected_header, converted_header)


class SystemDataTest(unittest.TestCase):
    def setUp(self):
        self.sys_dat = SystemData()

    def test_attribute_to_exist(self):
        self.assertTrue(hasattr(self.sys_dat, 'to'))

    def test_attribute_from_exist(self):
        self.assertTrue(hasattr(self.sys_dat, 'fromm'))

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

    def test_attribute_tries(self):
        self.assertTrue(hasattr(self.sys_dat, 'data_type'))

    def test_setter_from_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.fromm = data
        self.assertEquals(data, self.sys_dat.fromm)

    def test_setter_to_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.to = data
        self.assertEquals(data, self.sys_dat.to)

    def test_setter_id_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.id = data
        self.assertEquals(data, self.sys_dat.id)

    def test_setter_topic_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.topic = data
        self.assertEquals(data, self.sys_dat.topic)

    def test_setter_status_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.status = data
        self.assertEquals(data, self.sys_dat.status)

    def test_setter_update_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.update_time = data
        self.assertEquals(data, self.sys_dat.update_time)

    def test_setter_created_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.created_time = data
        self.assertEquals(data, self.sys_dat.created_time)

    def test_setter_scheduled_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.scheduled_time = data
        self.assertEquals(data, self.sys_dat.scheduled_time)

    def test_setter_error_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.error = data
        self.assertEquals(data, self.sys_dat.error)

    def test_setter_processed_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.processed_time = data
        self.assertEquals(data, self.sys_dat.processed_time)

    def test_setter_processing_time_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.processing_time = data
        self.assertEquals(data, self.sys_dat.processing_time)

    def test_setter_tries_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.tries = data
        self.assertEquals(data, self.sys_dat.tries)

    def test_setter_data_type_not_modifies_output(self):
        data = 'abc'
        self.sys_dat.data_type = data
        self.assertEquals(data, self.sys_dat.data_type)
