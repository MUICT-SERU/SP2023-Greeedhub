#!/usr/bin/env python

from distutils.core import setup

setup(name='Flask-JSONSchema-Ext',
      version='0.1.0',
      description='Flask JSONSchema Extended Library',
      author='rachekalmir',
      author_email='rachekalmir@users.noreply.github.com',
      url='https://github.com/rachekalmir/flask_jsonschema_ext',
      packages=['flask_jsonschema_ext'],
      install_requires=['sqlalchemy>=1.0.0', 'flask>=0.11.0', 'jsonschema>=2.6.0'],
      test_requirements=['pytest>=3.0'],
      )
