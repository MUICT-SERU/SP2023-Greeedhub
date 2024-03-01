from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.readlines()

setup(
    name='mongoengine_bundle',
    packages=find_packages(),
    version='1.4',
    description='mongoengine support for applauncher',
    author='Alvaro Garcia Gomez',
    author_email='maxpowel@gmail.com',
    url='https://github.com/applauncher-team/mongoengine_bundle',
    download_url='https://github.com/applauncher-team/mongoengine_bundle/archive/master.zip',
    keywords=['mongoengine', 'applauncher'],
    classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
    install_requires=install_requires,
    
)
