from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'column/$', views.lazy_column_view, name='lazy-column-view')
]
