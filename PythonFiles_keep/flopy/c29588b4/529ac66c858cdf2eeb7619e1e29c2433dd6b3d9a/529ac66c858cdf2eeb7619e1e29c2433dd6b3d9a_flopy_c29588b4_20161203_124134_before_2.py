"""
mf module.  Contains the ModflowGlobal, ModflowList, and Modflow classes.


"""

import os

from ..mbase import BaseModel
from ..modflow import Modflow


class LgrChild():
    def __init__(self, ishflg=1, ibflg=59, iucbhsv=0, iucbfsv=0,
                 mxlgriter=20, ioutlgr=1, relaxh=0.4, relaxf=0.4,
                 hcloselgr=5e-3, fcloselgr=5e-2,
                 nplbeg=0, nprbeg=0, npcbeg=0,
                 nplend=0, nprend=1, npcend=1,
                 ncpp=2, ncppl=1):
        self.ishflg = ishflg
        self.ibflg = ibflg
        self.iucbhsv = iucbhsv
        self.iucbfsv = iucbfsv
        self.mxlgriter = mxlgriter
        self.ioutlgr = ioutlgr
        self.relaxh = relaxh
        self.relaxf = relaxf
        self.hcloselgr = hcloselgr
        self.fcloselgr = fcloselgr
        self.nplbeg = nplbeg
        self.nprbeg = nprbeg
        self.npcbeg = npcbeg
        self.nplend = nplend
        self.nprend = nprend
        self.npcend = npcend
        self.ncpp = ncpp
        if isinstance(ncppl, int):
            self.ncppl = [ncppl]
        else:
            self.ncppl = ncppl


class ModflowLgr(BaseModel):
    """
    MODFLOW-LGR Model Class.

    Parameters
    ----------
    modelname : string, optional
        Name of model.  This string will be used to name the MODFLOW input
        that are created with write_model. (the default is 'modflowtest')
    namefile_ext : string, optional
        Extension for the namefile (the default is 'nam')
    version : string, optional
        Version of MODFLOW to use (the default is 'mf2005').
    exe_name : string, optional
        The name of the executable to use (the default is
        'mf2005').
    listunit : integer, optional
        Unit number for the list file (the default is 2).
    model_ws : string, optional
        model workspace.  Directory name to create model data sets.
        (default is the present working directory).
    external_path : string
        Location for external files (default is None).
    verbose : boolean, optional
        Print additional information to the screen (default is False).
    load : boolean, optional
         (default is True).
    silent : integer
        (default is 0)

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

    >>> import flopy
    >>> m = flopy.modflow.Modflow()

    """

    def __init__(self, modelname='modflowlgrtest', namefile_ext='lgr',
                 version='mflgr', exe_name='mflgr.exe',
                 parent=None, children=None, children_data=None, model_ws='.',
                 external_path=None,
                 verbose=False, **kwargs):
        BaseModel.__init__(self, modelname, namefile_ext, exe_name, model_ws,
                           structured=True, **kwargs)
        self.version_types = {'mflgr': 'MODFLOW-LGR'}

        self.set_version(version)

        # external option stuff
        self.array_free_format = True
        self.array_format = 'modflow'

        self.verbose = verbose

        self.parent = parent
        if children is not None:
            if not isinstance(children, list):
                children = [children]
        self.children = children
        if children_data is not None:
            if not isinstance(children_data, list):
                children_data = [children_data]
        self.children_data = children_data

        # set the number of grids
        self.children = 0
        if children is not None:
            self.children += len(children)

        self.load_fail = False
        # the starting external data unit number
        self._next_ext_unit = 2000

        if external_path is not None:
            if os.path.exists(os.path.join(model_ws, external_path)):
                print("Note: external_path " + str(external_path) +
                      " already exists")
            else:
                os.makedirs(os.path.join(model_ws, external_path))
        self.external_path = external_path
        self.verbose = verbose

        return

    def __repr__(self):
        return 'MODFLOW-LGR model with {} grids'.format(self.ngrids)

    @property
    def ngrids(self):
        try:
            return 1 + self.children
        except:
            return None

    def write_input(self, SelPackList=False, check=False):
        """
        Write the input. Overrides BaseModels's write_input

        Parameters
        ----------
        SelPackList : False or list of packages

        """
        if check:
            # run check prior to writing input
            pass

        if self.verbose:
            print('\nWriting packages:')

    @staticmethod
    def load(f, version='mflgr', exe_name='mflgr.exe', verbose=False,
             model_ws='.', load_only=None, forgive=True, check=True):
        """
        Load an existing model.

        Parameters
        ----------
        f : MODFLOW name file
            File to load.
        
        model_ws : model workspace path

        load_only : (optional) filetype(s) to load (e.g. ["bas6", "lpf"])

        forgive : flag to raise exception(s) on package load failure - good for debugging

        check : boolean
            Check model input for common errors. (default True)
        Returns
        -------
        ml : Modflow object

        Examples
        --------

        >>> import flopy
        >>> ml = flopy.modflow.Modflow.load(f)

        """
        # test if name file is passed with extension (i.e., is a valid file)
        if os.path.isfile(os.path.join(model_ws, f)):
            modelname = f.rpartition('.')[0]
        else:
            modelname = f

        if not hasattr(f, 'read'):
            filename = os.path.join(model_ws, f)
            f = open(filename, 'r')

        # dataset 0 -- header
        header = ''
        while True:
            line = f.readline()
            if line[0] != '#':
                break
            header += line.strip()

        # dataset 1
        ds1 = line.split()[0].lower()
        msg = 'LGR must be entered as the first item in dataset 1\n'
        msg += '  {}\n'.format(header)
        assert ds1 == 'lgr', msg

        # dataset 2
        line = f.readline()
        t = line.split()
        ngrids = int(t[0])
        nchildren = ngrids - 1

        # dataset 3
        line = f.readline()
        t = line.split()
        namefile = t[0]
        pws = os.path.join(model_ws, os.path.dirname(namefile))
        pn = os.path.basename(namefile)

        # dataset 4
        line = f.readline()
        t = line.split()
        gridstatus = t[0].lower()
        msg = "GRIDSTATUS for the parent must be 'PARENTONLY'"
        assert gridstatus == 'parentonly', msg

        # dataset 5
        line = f.readline()
        t = line.split()
        try:
            iupbhsv, iupbfsv = int(t[0]), int(t[1])
        except:
            msg = 'could not read dataset 5 - IUPBHSV and IUPBFSV.'
            raise ValueError(msg)

        # non-zero values for IUPBHSV and IUPBFSV in dataset 5 are not
        # supported
        if iupbhsv + iupbfsv > 0:
            msg = 'nonzero values for IUPBHSV () '.format(iupbhsv) + \
                  'and IUPBFSV ({}) '.format(iupbfsv) + \
                  'are not supported.'
            raise ValueError(msg)

        # load the parent model
        parent = Modflow.load(pn, verbose=verbose, model_ws=pws)

        children_data = []
        children = []
        for child in range(nchildren):
            # dataset 6
            line = f.readline()
            t = line.split()
            namefile = t[0]
            cws = os.path.join(model_ws, os.path.dirname(namefile))
            cn = os.path.basename(namefile)

            # dataset 7
            line = f.readline()
            t = line.split()
            gridstatus = t[0].lower()
            msg = "GRIDSTATUS for the parent must be 'CHILDONLY'"
            assert gridstatus == 'childonly', msg

            # dataset 8
            line = f.readline()
            t = line.split()
            ishflg, ibflg, iucbhsv, iucbfsv = int(t[0]), int(t[1]), int(t[2]), int(t[3])

            # dataset 9
            line = f.readline()
            t = line.split()
            mxlgriter, ioutlgr = int(t[0]), int(t[1])

            # dataset 10
            line = f.readline()
            t = line.split()
            relaxh, relaxf = float(t[0]), float(t[1])

            # dataset 11
            line = f.readline()
            t = line.split()
            hcloselgr, fcloselgr = float(t[0]), float(t[1])

            # dataset 12
            line = f.readline()
            t = line.split()
            nplbeg, nprbeg, npcbeg = int(t[0]) - 1, int(t[1]) - 1, int(t[2]) - 1

            # dataset 13
            line = f.readline()
            t = line.split()
            nplend, nprend, npcend = int(t[0]) - 1, int(t[1]) - 1, int(t[2]) - 1

            # dataset 14
            line = f.readline()
            t = line.split()
            ncpp = int(t[0])

            # dataset 15
            line = f.readline()
            t = line.split()
            ncppl = []
            for idx in range(nplend + 1 - nplbeg):
                ncppl.append(int(t[idx]))

            # build child data object

            children_data.append(LgrChild(ishflg=ishflg, ibflg=ibflg,
                                          iucbhsv=iucbhsv, iucbfsv=iucbfsv,
                                          mxlgriter=mxlgriter, ioutlgr=ioutlgr,
                                          relaxh=relaxh, relaxf=relaxf,
                                          hcloselgr=hcloselgr, fcloselgr=fcloselgr,
                                          nplbeg=nplbeg, nprbeg=nprbeg, npcbeg=npcbeg,
                                          nplend=nplend, nprend=nprend, npcend=npcend,
                                          ncpp=ncpp, ncppl=ncppl))
            # load child model
            children.append(Modflow.load(cn, verbose=verbose, model_ws=cws))

        lgr = ModflowLgr(modelname=modelname, model_ws=model_ws, verbose=verbose,
                         parent=parent,
                         children=children, children_data=children_data)

        # return model object
        return lgr
