from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^view_without_throttle$',            'app.views.view_without_throttle'),
    url(r'^view_with_throttle$',               'app.views.view_with_throttle'),
    url(r'^view_with_throttle_per_anonymous$', 'app.views.view_with_throttle_per_anonymous'),
    url(r'^view_with_throttle_all_anonymous$', 'app.views.view_with_throttle_all_anonymous'),
    url(r'^view_with_throttle_all_users$',     'app.views.view_with_throttle_all_users'),
    url(r'^view_with_throttle_role$',          'app.views.view_with_throttle_role'),
    url(r'^view_with_throttle_group$',         'app.views.view_with_throttle_group'),
    url(r'^view_with_throttle_all_in_group$',  'app.views.view_with_throttle_all_in_group'),
    
    url(r'^admin/', include(admin.site.urls)),
)
