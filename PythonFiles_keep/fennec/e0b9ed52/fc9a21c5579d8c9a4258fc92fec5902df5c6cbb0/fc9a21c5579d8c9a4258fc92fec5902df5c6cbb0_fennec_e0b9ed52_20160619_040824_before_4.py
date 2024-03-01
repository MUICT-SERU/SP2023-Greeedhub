from setuptools import setup, find_packages

setup_requires = []
install_requires = [
    "pytz",
]
setup(
    name='fennec',
    version='0.0.1',
    description='Simple data analysis toolbox in python.',
    author='Amane Suzuki',
    author_email='asuzuki@chemsys.t.u-tokyo.ac.jp',
    license='MIT',
    url='https://github.com/amaotone/fennec',
    packages=find_packages(),
    setup_requires=setup_requires,
    install_requires=install_requires
)
