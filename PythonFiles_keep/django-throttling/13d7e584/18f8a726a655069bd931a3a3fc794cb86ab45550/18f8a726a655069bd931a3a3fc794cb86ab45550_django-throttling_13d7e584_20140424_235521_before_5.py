#!/usr/bin/env python
# encoding: utf-8
from django.db.models import F, Count, Min
from django import models
from model_utils.managers import PassThroughManager
from .consts import COUNT_VALUE_AFTER_RESET
from datetime import datetime


class AccessQuerySet(models.query.QuerySet):
    
    def anonymous(self):
        return self.filter(consumer__ip__isnull=False)
    
    def increment_count(self):
        return self.update(count=F('count')+1)
        
    def reset_count(self):
        return self.update(count=COUNT_VALUE_AFTER_RESET, datemark=datetime.now())
        
    def count_request(self):
        return self.aggregate(count=Count('count'))['count']
        
    def min_datemark(self):
        return self.aggregate(min_date=Min('datemark'))['min_date']
