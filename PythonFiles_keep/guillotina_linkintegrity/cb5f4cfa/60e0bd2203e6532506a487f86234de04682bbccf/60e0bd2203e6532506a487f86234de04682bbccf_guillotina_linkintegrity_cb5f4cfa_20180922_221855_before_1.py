from setuptools import find_packages
from setuptools import setup


try:
    README = open('README.md').read()
except IOError:
    README = None

setup(
    name='guillotina_linkintegrity',
    version="1.0.0",
    description='Link integrity support for guillotina',
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=[
        'guillotina',
        'pypika',
        'lxml'
    ],
    author='Nathan Van Gheem',
    author_email='vangheem@gmail.com',
    url='https://github.com/guillotinaweb/guillotina_linkintegrity',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    tests_require=[
        'pytest',
    ],
    extras_require={
        'test': [
            'guillotina[test]'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
    }
)
