from setuptools import setup

setup(
    name='django-model-validator',
    packages=('model_validator',),
    author='C. Paschalides',
    author_email='already.late@gmail.com',
    description='A Django Mixin capable of converting dictionaries of data or lists of dictionaries, to clean Django model instances',
    url='https://github.com/stargazer/django-model-validator/',
    license='WTFPL',
    version=0.1,
    install_requires=(
        'Django',
    ),
    tests_require=('model_mommy'),
    test_suite='runtests',
    zip_safe=False,
    classifiers=(
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Freely Distributable'
    ),
)
