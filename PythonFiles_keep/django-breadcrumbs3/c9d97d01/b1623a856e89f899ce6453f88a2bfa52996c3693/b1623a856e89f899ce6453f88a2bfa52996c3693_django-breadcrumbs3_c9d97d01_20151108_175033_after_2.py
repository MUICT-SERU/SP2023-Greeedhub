from setuptools import find_packages, setup

from breadcrumbs3 import __version__

setup(
    name='django-breadcrumbs3',
    version=__version__,
    license='BSD',
    author='Sam Kingston',
    author_email='sam@sjkwi.com.au',
    description='Breadcrumbs app for Django',
    long_description='See https://github.com/sjkingo/django-breadcrumbs3 for the README',
    url='https://github.com/sjkingo/django-breadcrumbs3',
    install_requires=[
        'Django>=1.7',
    ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
