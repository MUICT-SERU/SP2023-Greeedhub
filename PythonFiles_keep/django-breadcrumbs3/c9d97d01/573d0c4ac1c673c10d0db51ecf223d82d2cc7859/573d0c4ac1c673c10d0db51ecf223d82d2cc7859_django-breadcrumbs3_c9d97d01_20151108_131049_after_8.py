from setuptools import find_packages, setup

from breadcrumbs3 import __version__

setup(
    name='django-breadcrumbs3',
    version=__version__,
    license='BSD',
    author='Sam Kingston',
    author_email='sam@sjkwi.com.au',
    description='Breadcrumbs app for Django',
    url='https://github.com/sjkingo/django-breadcrumbs3',
    install_requires=[
        'Django',
    ],
    packages=find_packages(),
)
