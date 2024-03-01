from setuptools import setup

setup(
    name='ctlogger',
    packages=['ctlogger'],
    version='0.0.3',
    description='A python log utils, such as colorful log on terminal, notify by slack or email',
    author='ChunTing Lin',
    author_email='sdf611097@gmail.com',
    url='https://github.com/sdf611097/py-logger',
    keywords='logger log color color-console notify slack sendgrid',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
    ],
    license='MIT',
    install_requires=['requests'],
)
