from .icy import preview
from .icy import read
from .icy import mem
from .icy import merge
from .icy import _path_to_objs
from .icy import run_examples
from .utils import str_remove_accents
from .utils import pdf_extract_text

from importlib.util import find_spec

ml_deps = [(p, find_spec(p)) for p in ['sklearn', 'xgboost', 'scipy', 'tables']]
if all([e[1] for e in ml_deps]):
    from icy.ml import crossval
    from icy.ml import explore
    from icy.ml import features
    from icy.ml import metrics
    from icy.ml import persist
    from icy.ml import prep
else:
    print('WARNING: dependencies {} for icy.ml missing, subpackage not available'.format( \
        ', '.join([e[0] for e in ml_deps if not e[1]])))

__version__ = '0.0.15'