from setuptools import setup, find_packages

try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = open('README.md').read()



setup(
    name='getinstance',
    version='0.2',
    description='getinstance',
    long_description=description,
    author='Roman Evstifeev',
    author_email='someuniquename@gmail.com',
    url='https://github.com/Fak3/getinstance',
    license='MIT',
    #packages=find_packages(),
    py_modules=['getinstance'],
    include_package_data=True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Android',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
