import unittest

from urllib3._collections import HTTPHeaderDict

from sciroccoclient.systemdata import SystemData, SystemDataHTTPSplitter


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


class SystemDataHTTPSplitterTest(unittest.TestCase):
    def setUp(self):
        self.system_headers_prefix = 'Scirocco'

        self.system_headers = ['Scirocco-To', 'Scirocco-Topic', 'Scirocco-Processed-Time', 'Scirocco-Processing-Time',
                               'Scirocco-From',
                               'Scirocco-Update-Time', 'Scirocco-Status', 'Scirocco-Tries', 'Scirocco-Id',
                               'Scirocco-Scheduled-Time', 'Scirocco-Created-Time', 'Scirocco-Error-Time']

        self.http_headers = HTTPHeaderDict()

        for h in self.system_headers:
            self.http_headers.add(h, 'hcontent')

        self.http_headers.add("Content-Type", "application/json")

        self.sample_splitter = SystemDataHTTPSplitter(SystemData(), self.http_headers)

    def test_attribute_http_system_headers_prefix_exists(self):
        self.assertTrue(hasattr(self.sample_splitter, 'http_system_headers_prefix'))

    def test_attribute_http_system_headers_prefix_fixed_value(self):
        self.assertEquals(self.system_headers_prefix, SystemDataHTTPSplitter.http_system_headers_prefix)

    def test_attribute_system_data_exists(self):
        self.assertTrue(hasattr(self.sample_splitter, 'system_data'))

    def test_attribute_http_headers_exists(self):
        self.assertTrue(hasattr(self.sample_splitter, 'http_headers'))

    def test_get_system_headers_exists(self):
        self.assertTrue("get_system_headers" in dir(self.sample_splitter))

    def test_extract_system_data_exists(self):
        self.assertTrue("extract_system_data" in dir(self.sample_splitter))

    def test_extract_http_headers_exists(self):
        self.assertTrue("extract_http_headers" in dir(self.sample_splitter))

    def test_number_of_get_system_headers(self):
        res = self.sample_splitter.get_system_headers()
        self.assertEqual(len(res), len(self.system_headers))

    def test_members_of_get_system_headers(self):
        res = self.sample_splitter.get_system_headers()

        same_headers = [i for i in res if i in self.system_headers]
        self.assertEqual(len(same_headers), len(self.system_headers))

    def test_extract_system_data_return_type(self):
        res = self.sample_splitter.extract_system_data()

        self.assertIsInstance(res, SystemData)

    def test_extract_system_data_check_return_object(self):
        res = self.sample_splitter.extract_system_data()
        self.assertEquals(res.id, 'hcontent')
        self.assertEquals(res.fromm, 'hcontent')
        self.assertEquals(res.to, 'hcontent')
        self.assertEquals(res.topic, 'hcontent')
        self.assertEquals(res.status, 'hcontent')
        self.assertEquals(res.created_time, 'hcontent')
        self.assertEquals(res.update_time, 'hcontent')
        self.assertEquals(res.error_time, 'hcontent')
        self.assertEquals(res.processed_time, 'hcontent')
        self.assertEquals(res.processing_time, 'hcontent')
        self.assertEquals(res.scheduled_time, 'hcontent')
        self.assertEquals(res.tries, 'hcontent')

    def test_extract_http_headers_check_return_type(self):
        res = self.sample_splitter.extract_http_headers()
        self.assertIsInstance(res, HTTPHeaderDict)

    def test_extract_http_headers_check_return_object(self):
        res = self.sample_splitter.extract_http_headers()
        self.assertEquals(res.get('Content-Type'), 'application/json')
        self.assertEquals(len(res), 1)
