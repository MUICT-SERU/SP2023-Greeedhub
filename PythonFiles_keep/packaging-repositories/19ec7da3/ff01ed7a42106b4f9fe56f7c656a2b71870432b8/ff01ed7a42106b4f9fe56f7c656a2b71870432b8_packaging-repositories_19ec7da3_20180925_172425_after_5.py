#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import py


ASYNC_DIR = py.path.local(os.path.abspath(__file__)).dirpath("async")


def pytest_ignore_collect(path, config):
    # Ignore async tests if not supported.
    if sys.version_info < (3, 5) and path.common(ASYNC_DIR) == ASYNC_DIR:
        return True
