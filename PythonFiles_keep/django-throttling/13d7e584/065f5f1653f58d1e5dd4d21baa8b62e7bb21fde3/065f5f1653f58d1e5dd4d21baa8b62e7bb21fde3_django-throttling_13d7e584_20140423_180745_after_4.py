#!/usr/bin/env python
# encoding: utf-8

from django.contrib              import admin
from yard.apps.throttling.models import Consumer, Access

admin.site.register( Access )
admin.site.register( Consumer )
