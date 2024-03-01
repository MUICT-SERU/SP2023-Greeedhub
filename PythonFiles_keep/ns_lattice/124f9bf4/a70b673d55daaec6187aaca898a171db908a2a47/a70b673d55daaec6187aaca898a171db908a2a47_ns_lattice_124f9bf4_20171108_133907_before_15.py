'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 13, 2017
@author: Niels Lubbes
'''
from nose import with_setup  # optional

from sage.all import *
from ns_lattice.class_ns_tools import NSTools

class TestClassNSTools:


    def test__p( self ):

        nt = NSTools()

        nt.filter( None )
        assert nt.p( 'Hello world!' ) != None

        nt.filter( 'another_class.py' )
        assert nt.p( 'No output since called from another class.' ) == None

        nt.filter_unset()
        assert nt.p( 'Filter is disabled so output this string.' ) != None

        nt.filter_reset()
        assert nt.p( 'Filter is enabled again so do not output.' ) == None

        nt.filter( 'test_class_ns_tools.py' )
        assert nt.p( 'Only output if called from this class' ) != None


    def test__tool_dct( self ):

        nt = NSTools()
        nt2 = NSTools()

        # watch out to not use the default file name
        # otherwise it might take long to load the data
        test_fname = 'test_tools'
        key = 'test__tool_dct'

        dct = nt.get_tool_dct( fname = test_fname )
        dct[key] = True
        nt.save_tool_dct( fname = test_fname )

        assert key in nt.get_tool_dct( fname = test_fname )
        assert key in nt2.get_tool_dct( fname = test_fname )

        nt.set_enable_tool_dct( False )
        assert key not in nt.get_tool_dct( fname = test_fname )
        assert key not in nt2.get_tool_dct( fname = test_fname )

        nt.set_enable_tool_dct( True )
        assert key in nt.get_tool_dct( fname = test_fname )
        assert key in nt2.get_tool_dct( fname = test_fname )


