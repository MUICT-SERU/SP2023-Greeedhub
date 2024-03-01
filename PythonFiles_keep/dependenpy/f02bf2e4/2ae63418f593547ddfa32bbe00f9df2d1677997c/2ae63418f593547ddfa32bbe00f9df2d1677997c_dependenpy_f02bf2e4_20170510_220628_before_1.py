# -*- coding: utf-8 -*-

"""
Dependenpy package.

With dependenpy you will be able to analyze the internal dependencies in
your Python code, i.e. which module needs which other module. You will then
be able to build a dependency matrix and use it for other purposes.
"""

from .dsm import DSM, Package, Module, Dependency


__author__ = 'Timothée Mazzucotelli <timothee.mazzucotelli@gmail.com>'
__version__ = '2.0.3'
__all__ = ('DSM', 'Package', 'Module', 'Dependency')
