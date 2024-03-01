#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class BaseScheduler(object):
    def __init__(self):
        pass

    def push(self, request):
        pass

    def poll(self):
        pass
