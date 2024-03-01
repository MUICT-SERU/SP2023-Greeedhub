from setuptools import find_packages, setup


version = '0.1.0'


setup(
    name='django-model-logging',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='Generic and secure logging for changes to Django model instances',
    long_description=open('README.md').read(),
    author='Incuna',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-model-logging/',
    install_requires=[],
    extras_require={},
    zip_safe=False,
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
    ],
)
