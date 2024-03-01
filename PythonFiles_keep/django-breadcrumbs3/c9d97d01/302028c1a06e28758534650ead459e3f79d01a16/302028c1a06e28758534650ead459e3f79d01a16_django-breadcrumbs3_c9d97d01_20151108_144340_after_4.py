from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^some_view_no_url/', some_view_no_url, name='test_no_url'),
    url(r'^some_view_with_url/', some_view_with_url, name='test_with_url'),
]
