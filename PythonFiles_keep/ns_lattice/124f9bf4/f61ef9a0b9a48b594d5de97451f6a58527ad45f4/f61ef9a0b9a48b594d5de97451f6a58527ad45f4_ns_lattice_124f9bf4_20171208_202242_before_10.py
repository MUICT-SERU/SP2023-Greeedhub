'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 9, 2017
@author: Niels Lubbes
'''

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_div import Div

from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_matrix
from ns_lattice.sage_interface import sage_ZZ

from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_ak

from ns_lattice.ns_basis import get_basis_lst


class TestNSBasis:

    def test__get_basis_lst( self ):

        NSTools.set_enable_tool_dct( False )

        a_lst = [ 'e0-e1', 'e0-e2']
        a_lst = [ Div.new( a, 4 ) for a in a_lst ]
        M = sage_identity_matrix( 4 )
        d_lst = []
        m1_lst = get_divs( get_ak( 4 ), 1, -1, True )

        bas_lst_lst = get_basis_lst( a_lst, M, d_lst, m1_lst )

        mat = sage_matrix( sage_ZZ, [ g.e_lst for g in bas_lst_lst[0] ] )
        print( list( mat ) )

        assert str( bas_lst_lst ) == '[(e0-e1, e0-e2, e3, e0-e1-e2)]'
        assert str( list( mat ) ) == '[(1, -1, 0, 0), (1, 0, -1, 0), (0, 0, 0, 1), (1, -1, -1, 0)]'

        NSTools.set_enable_tool_dct( True )


