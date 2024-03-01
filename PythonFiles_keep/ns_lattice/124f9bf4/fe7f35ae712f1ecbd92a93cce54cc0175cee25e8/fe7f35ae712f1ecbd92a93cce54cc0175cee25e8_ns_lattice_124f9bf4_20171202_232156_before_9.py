'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 7, 2017
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_matrix
from ns_lattice.class_div import Div

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_dp_lattice import DPLattice


class TestClassDiv:


    def test__get_cls_real_dp__rank_4( self ):
        NSTools.set_enable_tool_dct( False )

        dct = DPLattice.get_cls_real_dp( 3 )
        print( dct.keys() )
        for dpl in dct[3]:
            print( dpl )

        assert { ( dpl.Mtype, dpl.type ) for dpl in dct[3] } == { ( 'A0', 'A0' ), ( 'A0', 'A1' ), ( 'A1', 'A0' )}
        NSTools.set_enable_tool_dct( True )


