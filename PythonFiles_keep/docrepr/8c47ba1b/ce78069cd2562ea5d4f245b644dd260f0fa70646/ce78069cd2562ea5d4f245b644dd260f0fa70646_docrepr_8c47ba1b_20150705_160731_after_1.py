# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 Tim Dumol 
# Copyright (c) 2012- Spyder Development team
#
# Licensed under the terms of the MIT or BSD Licenses
# (See every file for its license)

"""
Docrepr library

Library to generate rich and plain representations of docstrings,
including several metadata of the object to which the docstring
belongs

Derived from spyderlib.utils.inspector and IPython.core.oinspect
"""

# Configuration options for docrepr
options = {
    'render_math': True,
    'local_mathjax': False,
    'collapse_sections': False,
    'use_qt4': False,
    'outline': False
}
