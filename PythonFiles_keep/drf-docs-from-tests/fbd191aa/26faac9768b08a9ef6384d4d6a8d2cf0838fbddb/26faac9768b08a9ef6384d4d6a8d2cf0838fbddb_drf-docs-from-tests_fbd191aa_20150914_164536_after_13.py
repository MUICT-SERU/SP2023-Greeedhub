# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from docsfromtests.testcase import DocAPITestCase


class UserTests(DocAPITestCase):
    caption = u'My test'
    description = u'Description test test'

    def test_get_users(self):
        u''' Get users '''
        self.doc(u'фывфыв')
        url = reverse('user-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        u''' Test create user '''
        url = reverse('user-list')
        data = {'username': 'test', 'password': '123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
