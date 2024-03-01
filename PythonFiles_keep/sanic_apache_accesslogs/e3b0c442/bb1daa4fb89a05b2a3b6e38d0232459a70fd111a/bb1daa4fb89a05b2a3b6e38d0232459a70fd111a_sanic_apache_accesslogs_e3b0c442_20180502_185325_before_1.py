
import codecs
import os

from setuptools import setup


__version__ = '0.1.2'


def open_local(paths, mode='r', encoding='utf8'):
    path = os.path.join(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            *paths
        )
    )

    return codecs.open(path, mode, encoding)


with open_local(['requirements.txt']) as req:
    install_requires = req.read().split("\n")


# http://peterdowns.com/posts/first-time-with-pypi.html
setup(
    name='sanic_access_logs',
    packages=['sanic_access_logs'],
    version=__version__,
    description='Apache Access Logs for Sanic',
    author='Arnulfo Solis',
    author_email='arnulfojr94@gmail.com',
    url='https://github.com/arnulfojr/sanic-apache-access-logs',
    download_url='https://github.com/arnulfojr/sanic-apache-access-logs/archive/{}.tar.gz'.format(__version__),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=install_requires,
    keywords=['accesslog', 'access', 'logs', 'sanic', 'plugin'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

