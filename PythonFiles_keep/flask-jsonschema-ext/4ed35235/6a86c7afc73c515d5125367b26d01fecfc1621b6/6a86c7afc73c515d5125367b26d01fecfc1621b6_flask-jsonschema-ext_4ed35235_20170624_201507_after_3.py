#!/usr/bin/env python
"""
Flask JSONSchema Extended Library

This library can be used to apply a JSONSchema (http://json-schema.org/) to a Flask API end-point that is generated on the fly from your database entities.

Currently supported drivers are:

* SQLAlchemy
"""

from setuptools import setup

from flask_jsonschema_ext import __version__

setup(name='Flask-JSONSchema-Ext',
      version=__version__,
      license='MIT',
      description='Flask JSONSchema Extended Library',
      long_description=__doc__,
      author='rachekalmir',
      author_email='rachekalmir@users.noreply.github.com',
      url='https://github.com/rachekalmir/flask-jsonschema-ext',
      packages=['flask_jsonschema_ext'],
      install_requires=['sqlalchemy>=1.0.0', 'flask>=0.11.0', 'jsonschema>=2.6.0'],
      tests_requires=['pytest>=2.5.2', 'pytest-cache>=1.0', 'pytest-cov>=1.6', 'pytest-flakes>=0.2', 'tox>=1.7.0'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      )
