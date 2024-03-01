#!/usr/bin/env python
# encoding: utf-8
from django.db import models
from django.contrib.auth.models import User
from model_utils.managers import PassThroughManager
from .managers import AccessQuerySet
from .consts import COUNT_VALUE_AFTER_RESET, DEFAULT_COUNT_VALUE
from datetime import datetime


class Consumer(models.Model):
    '''
    Represents an authenticated ou anonymous web client
    '''
    user = models.ForeignKey(User, blank=True, null=True)
    ip   = models.IPAddressField(blank=True, null=True)

    class Meta:
        unique_together =  (('user', 'ip', 'all_anonymous'),)


class Access(models.Model):
    '''
    Relates the Consumer with the scope
    '''
    consumer = models.ForeignKey(Consumer)
    scope    = models.CharField(max_length=100)
    count    = models.IntegerField(default=DEFAULT_COUNT_VALUE)
    datemark = models.DateTimeField(blank=True, default=datetime.now)
    objects  = PassThroughManager.for_queryset_class(AccessQuerySet)()

    def count_request(self):
        return self.count

    def min_datemark(self):
        return self.datemark

    def increment_count(self):
        self.count += 1
        self.save()

    def reset_count(self):
        self.count = COUNT_VALUE_AFTER_RESET
        self.datemark = datetime.now()
        self.save()

    class Meta:
        unique_together =  (('consumer', 'scope'),)
