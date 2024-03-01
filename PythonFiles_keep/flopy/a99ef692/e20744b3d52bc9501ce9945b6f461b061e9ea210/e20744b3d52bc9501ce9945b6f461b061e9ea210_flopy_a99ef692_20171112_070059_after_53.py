from .. import mfpackage
from ..data import mfdatautil


class ModflowGwfdis(mfpackage.MFPackage):
    package_abbr = "gwfdis"
    delr = mfdatautil.ArrayTemplateGenerator(('gwf6', 'dis', 'griddata', 'delr'))
    delc = mfdatautil.ArrayTemplateGenerator(('gwf6', 'dis', 'griddata', 'delc'))
    top = mfdatautil.ArrayTemplateGenerator(('gwf6', 'dis', 'griddata', 'top'))
    botm = mfdatautil.ArrayTemplateGenerator(('gwf6', 'dis', 'griddata', 'botm'))
    idomain = mfdatautil.ArrayTemplateGenerator(('gwf6', 'dis', 'griddata', 'idomain'))
    """
    ModflowGwfdis defines a dis package within a gwf6 model.

    Attributes
    ----------
    length_units : (length_units : string)
        is the length units used for this model. Values can be ``FEET'', ``METERS'', or ``CENTIMETERS''. If not specified, the default is ``UNKNOWN''.
    nogrb : (nogrb : keyword)
        keyword to deactivate writing of the binary grid file.
    xorigin : (xorigin : double)
        x-position of the lower-left corner of the model grid. A default value of zero is assigned if not specified. The value for xorigin does not affect the model simulation, but it is written to the binary grid file so that postprocessors can locate the grid in space.
    yorigin : (yorigin : double)
        y-position of the lower-left corner of the model grid. If not specified, then a default value equal to zero is used. The value for yorigin does not affect the model simulation, but it is written to the binary grid file so that postprocessors can locate the grid in space.
    angrot : (angrot : double)
        counter-clockwise rotation angle (in degrees) of the lower-left corner of the model grid. If not specified, then a default value of 0.0 is assigned. The value for angrot does not affect the model simulation, but it is written to the binary grid file so that postprocessors can locate the grid in space.
    nlay : (nlay : integer)
        is the number of layers in the model grid.
    nrow : (nrow : integer)
        is the number of rows in the model grid.
    ncol : (ncol : integer)
        is the number of columns in the model grid.
    delr : [(delr : double)]
        is the is the column spacing in the row direction.
    delc : [(delc : double)]
        is the is the row spacing in the column direction.
    top : [(top : double)]
        is the top elevation for each cell in the top model layer.
    botm : [(botm : double)]
        is the bottom elevation for each cell.
    idomain : [(idomain : integer)]
        is an optional array that characterizes the existence status of a cell. If the idomain array is not specified, then all model cells exist within the solution. If the idomain value for a cell is 0, the cell does not exist in the simulation. Input and output values will be read and written for the cell, but internal to the program, the cell is excluded from the solution. If the idomain value for a cell is 1, the cell exists in the simulation. If the idomain value for a cell is -1, the cell does not exist in the simulation. Furthermore, the first existing cell above will be connected to the first existing cell below. This type of cell is referred to as a ``vertical pass through'' cell.

    """
    def __init__(self, model, add_to_package_list=True, length_units=None, nogrb=None, xorigin=None, yorigin=None,
                 angrot=None, nlay=None, nrow=None, ncol=None, delr=None, delc=None, top=None,
                 botm=None, idomain=None, fname=None, pname=None, parent_file=None):
        super(ModflowGwfdis, self).__init__(model, "dis", fname, pname, add_to_package_list, parent_file)        

        # set up variables
        self.length_units = self.build_mfdata("length_units", length_units)

        self.nogrb = self.build_mfdata("nogrb", nogrb)

        self.xorigin = self.build_mfdata("xorigin", xorigin)

        self.yorigin = self.build_mfdata("yorigin", yorigin)

        self.angrot = self.build_mfdata("angrot", angrot)

        self.nlay = self.build_mfdata("nlay", nlay)

        self.nrow = self.build_mfdata("nrow", nrow)

        self.ncol = self.build_mfdata("ncol", ncol)

        self.delr = self.build_mfdata("delr", delr)

        self.delc = self.build_mfdata("delc", delc)

        self.top = self.build_mfdata("top", top)

        self.botm = self.build_mfdata("botm", botm)

        self.idomain = self.build_mfdata("idomain", idomain)


