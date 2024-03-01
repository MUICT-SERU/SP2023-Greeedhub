#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Matthew Rankin on 2010-11-16.
Copyright (c) 2010 Matthew Rankin. All rights reserved.
"""

import os

def find_filenames_with_extensions(
        search_directory, extensions):
    files_found = []
    for root, dirs, files in os.walk(search_directory):
        for filename in files:
            current_file = os.path.join(root, filename)
            for extension in extensions:
                if filename.endswith(extension):
                    files_found.append(current_file)
    return files_found
