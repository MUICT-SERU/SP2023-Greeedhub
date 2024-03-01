from invoke import run, task


@task
def clean(docs=False, bytecode=False, extra=''):
    patterns = ['build']
    if docs:
        patterns.append('docs/_build')
    if bytecode:
        patterns.append('**/*.pyc')
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        run("rm -rf {files}".format(files=pattern))


@task
def build(docs=False):
    """
    Bump versions and prepare for PyPI
    """
    run("python setup.py build")
    if docs:
        run("sphinx-build docs docs/_build")


@task
def upload():
    """
    Upload dirwalker to PyPI
    """
    run("python setup.py register sdist upload")
