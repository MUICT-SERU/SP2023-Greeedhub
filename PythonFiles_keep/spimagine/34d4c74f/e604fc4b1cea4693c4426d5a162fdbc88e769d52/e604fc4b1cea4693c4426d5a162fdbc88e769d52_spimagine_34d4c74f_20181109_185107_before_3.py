import sys
import os
sys.path.append(os.path.split(os.path.abspath(__file__))[0])
from hook_utils import _get_toc_objects


import pyopencl

__PATH__ = os.path.dirname(pyopencl.__file__)


datas = _get_toc_objects(os.path.join(__PATH__, "cl/"),
                       dir_prefix = "pyopencl/cl")


print "\n"*5
print datas
print "\n"*5
