"""
    the main entry point of utils

    Parameters
    ----------

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    """
from .mfreadnam import parsenamefile
from .util_array import util_3d, util_2d, transient_2d, read1d
from .util_list import mflist
from .binaryfile import BinaryHeader, HeadFile, UcnFile, CellBudgetFile
from .modpathfile import PathlineFile, EndpointFile
from .binaryswrfile import SwrObs, SwrFile
from .binaryhydmodfile import HydmodObs
from .reference import SpatialReference  # , TemporalReference
from .flopy_io import model_attributes_to_shapefile, shape_attr_name, write_grid_shapefile
from .mflistfile import MfListBudget, MfusgListBudget, SwtListBudget, \
    SwrListBudget, ListTime
