import codecs
import os

from setuptools import setup


__version__ = '0.2.1'


URL = 'https://github.com/arnulfojr/sanic_apache_accesslogs'


def open_local(paths, mode='r', encoding='utf8'):
    path = os.path.join(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            *paths
        )
    )

    return codecs.open(path, mode, encoding)


with open_local(['README.md']) as readme:
    long_description = readme.read()


with open_local(['requirements.txt']) as req:
    install_requires = req.read().split("\n")


# http://peterdowns.com/posts/first-time-with-pypi.html
setup(
    name='sanic_apache_accesslogs',
    packages=['sanic_apache_accesslogs'],
    version=__version__,
    description='Apache Access Logs for Sanic',
    long_description=long_description,
    author='Arnulfo Solis',
    author_email='arnulfojr94@gmail.com',
    url=URL,
    download_url='{}/archive/{}.tar.gz'.format(URL, __version__),
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
