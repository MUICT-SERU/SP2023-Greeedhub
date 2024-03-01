# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='Flask-Filtered-Response',
    version='1.0.1',
    url='https://github.com/vrcmarcos/flask-filtered-response',
    license='MIT',
    author='Marcos Cardoso',
    author_email='vrcmarcos@gmail.com',
    description='Add filter capability to JSON responses',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.11.1',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
