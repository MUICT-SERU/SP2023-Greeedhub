import glob
import io
import os
import sys

import pytest

try:
    import jupyter_client
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
except ImportError:
    pytest.mark.skip(reason='Required packages not available')

kernels = jupyter_client.kernelspec.find_kernel_specs()
kernel_name = 'python%s' % sys.version_info.major

head, _ = os.path.split(__file__)
NOTEBOOK_DIR = os.path.abspath(os.path.join(head, '..', '..', 'examples'))
print(NOTEBOOK_DIR)

nbs = sorted(glob.glob(os.path.join(NOTEBOOK_DIR, '*.ipynb')))
ids = list(map(lambda s: os.path.split(s)[-1].split('.')[0], nbs))
if not nbs:
    pytest.mark.skip(reason='No notebooks found so not tests run')


@pytest.fixture(params=nbs, ids=ids)
def notebook(request):
    return request.param


def test_notebook(notebook):
    with io.open(notebook, encoding='utf-8') as f:
        nb = nbformat.read(notebook, as_version=4)

    ep = ExecutePreprocessor(allow_errors=False,
                             timeout=20,
                             kernel_name=kernel_name)
    ep.preprocess(nb, {'metadata': {'path': NOTEBOOK_DIR}})
