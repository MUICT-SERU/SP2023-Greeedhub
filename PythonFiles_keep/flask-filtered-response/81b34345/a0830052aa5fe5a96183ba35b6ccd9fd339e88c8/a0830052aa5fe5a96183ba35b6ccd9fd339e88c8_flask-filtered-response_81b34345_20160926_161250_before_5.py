# -*- coding: utf-8 -*-

import json
from unittest import TestCase

from tests import app


class TestPaginatedResponse(TestCase):

    def setUp(self):
        self.test_client = app.test_client()

    def test_should_return_all_content_when_no_filter_is_set_up_in_single_node_response(self):
        response = self.test_client.get('/filtered/single_node')
        response_dict = json.loads(response.data)
        self.assertDictEqual({
            'test_int': 123,
            'test_string': 'Hey!',
        }, response_dict)

    def test_should_return_only_test_int_when_filter_is_set_up_to_test_int_only_in_single_node_response(self):
        response = self.test_client.get('/filtered/single_node?fields=test_int')
        response_dict = json.loads(response.data)
        self.assertDictEqual({
            'test_int': 123,
        }, response_dict)

    def test_should_return_all_content_when_no_filter_is_set_up_in_multiple_nodes_response(self):
        response = self.test_client.get('/filtered/multiple_nodes')
        response_list = json.loads(response.data)
        self.assertListEqual([
            {
                'test_int': 123,
                'test_string': 'Hey!',
            },
            {
                'test_int': 456,
                'test_string': 'Yo!',
            },
        ], response_list)

    def test_should_return_only_test_string_when_filter_is_set_up_to_test_string_in_multiple_nodes_response(self):
        response = self.test_client.get('/filtered/multiple_nodes?fields=test_string')
        response_list = json.loads(response.data)
        self.assertListEqual([
            {
                'test_string': 'Hey!',
            },
            {
                'test_string': 'Yo!',
            },
        ], response_list)
