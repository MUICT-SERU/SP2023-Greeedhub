from distutils.core import setup

setup(
    name='DirWalker',
    version='0.1',
    author='Matthew Rankin',
    author_email='matthew.d.rankin@gmail.com',
    url='https://github.com/matthewrankin'
    license='BSD',
    description='Directory Walker',
    long_description=open('README.txt').read(),
    py_modules=['dirwalker'],
    classifiers=[
        'Programming Language :: Python',
        'License :: BSD',
        'Operation System :: OS Independent',
    ]
)