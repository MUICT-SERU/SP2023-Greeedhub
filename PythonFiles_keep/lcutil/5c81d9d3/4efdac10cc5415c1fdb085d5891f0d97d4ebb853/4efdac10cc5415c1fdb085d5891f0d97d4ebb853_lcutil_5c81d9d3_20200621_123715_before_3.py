from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


# https://pypi.org/pypi?%3Aaction=list_classifiers
setup(name='lcutil',
      version='0.2.2',
      description='General useful utility functions for Python projects.',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
      ],
      keywords='utility functions devel',
      url='http://github.com/lcordier/lcutil/',
      author='Louis Cordier',
      author_email='lcordier@gmail.com',
      license='MIT',
      packages=['lcutil'],
      install_requires=[
          'imapclient',
          'pyzmail',
          'unidecode',
          'ftputil',
          'paramiko',
          'pillow',
          'logging_tree',
      ],
      # test_suite='nose.collector',
      # tests_require=['nose', 'nose-cover3'],
      entry_points={
          'console_scripts': [
              'find_between=lcutil.find_between:main',
              'imap_tool=lcutil.imap_tool:main',
              'send_email=lcutil.send_email:main',
          ],
      },
      include_package_data=True,
      zip_safe=False)
