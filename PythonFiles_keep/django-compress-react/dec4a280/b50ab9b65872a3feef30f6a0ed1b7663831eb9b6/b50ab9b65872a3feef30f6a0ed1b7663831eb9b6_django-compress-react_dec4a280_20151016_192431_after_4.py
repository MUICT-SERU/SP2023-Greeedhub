# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

description = """
django-compressor compressor for react
"""

setup(
    name='django-compress-react',
    version='0.0.1',
    description=description,
    long_description=description,
    author='tekton',
    author_email='tyler@pyroturtle.com',
    url='https://github.com/tekton/django-compress-react',
    packages=find_packages(),
    zip_safe=False,
    install_requires=["PyReact", "django-compressor"],
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
