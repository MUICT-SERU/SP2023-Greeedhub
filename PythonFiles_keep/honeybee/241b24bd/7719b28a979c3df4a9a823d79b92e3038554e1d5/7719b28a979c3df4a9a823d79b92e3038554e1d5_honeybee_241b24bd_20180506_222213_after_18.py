"""Run test units."""
import os
import subprocess


def main(verbose=True, test_files=None, path_to_python="c:/python27"):
    """Execute all test files inside tests folder."""
    # change directory to the file directory. The file should be in root directory
    _curdir = os.path.dirname(__file__)
    # os.chdir(_curdir)

    if not test_files:
        # find all files in tests folder
        test_files = [f[:-3] for f in os.listdir('./tests')
                      if f[-3:] == ".py" and f[0] != "_"]

    # edit __init__ file inside tests folder
    with open(os.path.join(_curdir, "tests/__init__.py"), "w") as initf:
        initf.write("import " + ",".join(test_files))

    # execute each test file
    cmd_base = '%s/python -m unittest -v tests.%s'
    if not verbose:
        cmd_base = cmd_base.replace("-v", "")

    for f in test_files:
        print("running test for %s" % f)
        cmd = cmd_base % (path_to_python, f)
        subprocess.Popen(cmd, shell=True)


if __name__ == "__main__":
    import sys
    print("Running tests...")
    test_files = []
    main(verbose=False, test_files=test_files)
