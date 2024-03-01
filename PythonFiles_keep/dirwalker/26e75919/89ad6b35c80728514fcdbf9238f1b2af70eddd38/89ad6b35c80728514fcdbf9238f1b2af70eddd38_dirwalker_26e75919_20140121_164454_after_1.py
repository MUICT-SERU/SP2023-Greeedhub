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
def lint():
    run("python setup.py flake8")


@task
def upload():
    """
    Upload dirwalker to PyPI
    """
    run("python setup.py register sdist upload")


@task()
def release(start=False, finish=False, deploy=False, version=''):
    if start:
        if version:
            run("git flow release start v{ver}".format(
                ver=version))
    if finish:
        if deploy:
            if version:
                run("python setup.py check")
                run("python setup.py sdist")
                run("git flow release finish v{ver}".format(
                    ver=version))
                run("git push --tags")
                run("git checkout master")
                run("python setup.py register sdist upload")
                run("git check develop")
        else:
            print("* Have you updated the version in dirwalker.py?")
            print("* Have you updated CHANGES.md?")
            print("* Have you fixed any last minute bugs?")
            print("If you answered yes to all of the above questions,")
            print("then run `invoke release --finish --deploy -vX.YY`")
