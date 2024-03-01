from setuptools import setup, find_packages

setup(name='redisGroupMsg',
      version='0.0.5',
      description='This is a packet that broadcasts redis multiple queues',
      url='https://github.com/zhenruyan/redisGroupMsg',
      author='zhenruyan',
      author_email='baiyangwangzhan@hotmail.com',
      license='WTFPL',
      packages=find_packages(),
      zip_safe=False,
      platforms=["all"],
      long_description=open('README.rst').read(),
classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],install_requires=[
        'redis==3.0.1'
    ]
      )
