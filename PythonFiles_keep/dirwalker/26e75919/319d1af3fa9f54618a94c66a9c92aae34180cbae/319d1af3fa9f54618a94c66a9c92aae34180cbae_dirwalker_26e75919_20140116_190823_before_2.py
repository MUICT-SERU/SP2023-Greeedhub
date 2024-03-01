from setuptools import setup

setup(
    name='dirwalker',
    version='0.1.2',
    author='Matthew Rankin',
    author_email='matthew@questrail.com',
    py_modules=['dirwalker'],
    url='https://github.com/matthewrankin/dirwalker',
    license='LICENSE.txt',
    description='Python Directory Walker module',
    long_description=open('README.md').read(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    setup_requires=[
        'flake8'
    ]
)
