import os

from setuptools import setup
import re
import sciroccoclient

here = os.path.abspath(os.path.dirname(__file__))

try:

    with open(here + '/README.md') as r:
        readme_html = r.read()
        readme_plain = re.sub(r"<([0-9a-zA-Z/]*)>", "", readme_html)

    with open(here + '/requirements.txt') as req:
        reqs = req.read().splitlines()
except:

    reqs = list()
    readme_plain = ''

setup(
    name='scirocco-pyclient',
    version=sciroccoclient.__version__,
    download_url='https://github.com/eloylp/scirocco-pyclient/tarball/' + sciroccoclient.__version__,
    url='https://github.com/eloylp/scirocco-pyclient',
    license='GNU AFFERO 3',
    author='eloylp',
    install_requires=reqs,
    author_email='eloy@sandboxwebs.com',
    description='Client library for scirocco proyect.',
    test_suite='test',
    long_description=readme_plain,
    packages=['sciroccoclient', 'sciroccoclient.http'],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: System :: Networking :: Monitoring',
        'License :: Freely Distributable',
        'Operating System :: POSIX :: Linux'
    ],
    include_package_data=True,
    platforms='any'
)
