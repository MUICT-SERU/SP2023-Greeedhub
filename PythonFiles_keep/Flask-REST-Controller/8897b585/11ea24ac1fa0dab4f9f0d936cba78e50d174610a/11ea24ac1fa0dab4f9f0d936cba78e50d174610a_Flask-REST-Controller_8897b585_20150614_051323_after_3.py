#!/usr/bin/env python
"""
Flask-REST-Controller
=====================


Flask-REST-Controller is added Class-Based-View(Controller) extension on
`Flask <http://flask.pocoo.org/>`__

Features
--------

-  Follow the RESTful design
-  provide of prepare authentication and request validation

   -  other class based view library is not provided of validation

-  uniform routing management

   -  The existing functional view is difficult to manage. Definition
      routing Scattered

-  JSON Response Validation with JSON Schema

   -  It would be useful for creating an API :)

Installation
------------

::

    $ pip install flask-rest-controller

Usage
-----

.. code:: python

    from flask import Flask
    from flask_rest_controller import Controller, set_routing

    app = Flask(__name__)
    app.secret_key = '\xcd\x8f\x10\x8a|\x10\t\xe8g<\xce|\xc7\xe6\xe3h\x8e\xd6\xfa\xc8i|\xee\xb0'


    class JsonController(Controller):
        schema = {
            'GET': {
                'type': 'array',
                'properties': {
                    'id':   {
                        'type': 'string'
                    }
                }
            },
            'POST': {
                'type': 'object',
                'properties': {
                    'result':   {
                        'type': 'string'
                    },
                    'code': {
                        'type': 'integer'
                    }
                }
            }
        }

        def get(self):
            return self.render_json(["Hello World"])

        def post(self):
            return self.render_json({'result': "ok", 'code': 200})

    ROUTING = [
        ("/", "app.JsonController", "json_controller"),
    ]

    set_routing(app, ROUTING)

    if __name__ == "__main__":
        app.run(debug=True)

Just save it as app.py and try

.. code:: bash

    $ python app.py

Now head over to http://127.0.0.1:5000/, and you should see your hello
world of json string

You should see a post request result, try this command

.. code:: bash

    $ curl --request POST http://127.0.0.1:5000

You should see that you json in the post method

see
https://github.com/teitei-tk/Flask-REST-Controller/tree/master/example
For other examples

Dependencies
------------

-  Python2.6 later
-  jsonschema

Contribute
----------

1. Fork it
2. Create your feature branch (``git checkout -b your-new-feature``)
3. Commit your changes (``git commit -am 'Added some feature'``)
4. Push to the branch (``git push origin your-new-feature``)
5. Create a new Pull Request

LICENSE
-------

-  MIT

"""

try:
    import setuptools
    from setuptools import setup, find_packages
except ImportError:
    import sys
    print("Please install setuptools.")
    sys.exit(1)

import version

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Flask',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries',
]

setup(
    name='Flask-REST-Controller',
    version=version.VERSION,
    description='Flask-REST-Controller is added Class-Based-View(Controller) extension on Flask',
    long_description=__doc__,
    author='teitei-tk',
    author_email='teitei.tk@gmail.com',
    url='https://github.com/teitei-tk/Flask-REST-Controller',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    classifiers=classifiers,
    install_requires=open('requirements.txt').read().splitlines(),
    keywords=['flask', 'controller', 'view', 'cbv'],
    download_url='https://github.com/teitei-tk/Flask-REST-Controller/archive/master.tar.gz'
)
