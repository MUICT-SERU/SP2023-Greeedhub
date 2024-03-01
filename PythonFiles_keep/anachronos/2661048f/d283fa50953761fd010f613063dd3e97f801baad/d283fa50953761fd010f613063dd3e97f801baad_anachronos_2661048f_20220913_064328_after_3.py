from os import path
from subprocess import check_output

from setuptools import setup, find_packages

git_version_command = 'git describe --tags --long --dirty'
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def read_version_from_git() -> str:
    try:
        version_string = check_output(git_version_command.split()).decode('utf-8').strip().split("-")
        dirty = version_string[1] != "0"
        if dirty:
            return f"{version_string[0]}+{version_string[2]}"
        return version_string[0]

    except:
        return "0.0.0"

if path.exists(here + "/.git"):
    init_file = None
    with open(path.join(here, 'anachronos/__init__.py'), 'r', encoding='utf-8') as f:
        init_file = f.read()
    if "@@VERSION@@" in init_file:
        with open(path.join(here, 'anachronos/__init__.py'), 'w', encoding='utf-8') as f:
            f.write(init_file.replace("@@VERSION@@", read_version_from_git()))

import anachronos

setup(
    name='anachronos',
    version=anachronos.__version__,
    setup_requires=[],
    description='A testing framework for testing frameworks.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/keotl/anachronos',

    author='Kento A. Lauzon',
    author_email='kento.lauzon@ligature.ca',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    packages=find_packages(
        exclude=['example', 'tests', 'tests.*']),

    install_requires=[],
)
