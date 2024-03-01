from invoke import run, task


@task
def lint():
    run("python setup.py flake8")


@task(pre=['lint'])
def test():
    run("nosetests")


@task()
def release(start=False, finish=False, deploy=False, version=''):
    """Release dirwalker and deploy to PyPI
    """
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
                run("git checkout develop")
        else:
            print("* Have you updated the version in dirwalker.py?")
            print("* Have you updated CHANGES.md?")
            print("* Have you fixed any last minute bugs?")
            print("If you answered yes to all of the above questions,")
            print("then run `invoke release --finish --deploy -vX.YY`")
