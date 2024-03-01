'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 9, 2017
@author: Niels Lubbes
'''

import sys

from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_matrix
from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_register_unpickle_override

from ns_lattice.class_div import Div

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_dp_lattice import DPLattice

from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_ak

from ns_lattice.ns_basis import get_bases_lst
from ns_lattice.ns_basis import get_webs



class TestNSBasis( object ):

    def test__get_basis_lst__rank_4__False( self ):

        NSTools.set_enable_tool_dct( False )

        rank = 4

        # construct DPLattice
        d_lst = []
        Md_lst = []
        M = sage_identity_matrix( rank )
        dpl = DPLattice( d_lst, Md_lst, M )

        # change basis
        a_lst = [ 'e0-e1', 'e0-e2']
        a_lst = [ Div.new( a, rank ) for a in a_lst ]
        m1_lst = get_divs( get_ak( rank ), 1, -1, True )
        d_tup_lst = get_bases_lst( a_lst, M, d_lst, m1_lst, False )

        B = sage_matrix( sage_ZZ, [ d.e_lst for d in d_tup_lst[0] ] )
        dplB = dpl.get_basis_change( B )
        int_mat = list( dplB.m1_lst[0].int_mat )

        print( dplB )

        print( str( d_tup_lst ) )
        assert str( d_tup_lst ) == '[(e0-e1, e0-e2, e3, e0-e1-e2)]'

        print( list( B ) )
        assert str( list( B ) ) == '[(1, -1, 0, 0), (1, 0, -1, 0), (0, 0, 0, 1), (1, -1, -1, 0)]'

        print( str( int_mat ) )
        assert str( int_mat ) == '[(0, 1, 0, 0), (1, 0, 0, 0), (0, 0, -1, 0), (0, 0, 0, -1)]'


        NSTools.set_enable_tool_dct( True )


    def test__get_basis_lst__rank_4__True( self ):

        NSTools.set_enable_tool_dct( False )


        rank = 4

        # construct DPLattice
        d_lst = []
        Md_lst = []
        M = sage_identity_matrix( rank )
        dpl = DPLattice( d_lst, Md_lst, M )

        # change basis
        a_lst = [ 'e0-e1', 'e0-e2']
        a_lst = [ Div.new( a, rank ) for a in a_lst ]
        m1_lst = get_divs( get_ak( rank ), 1, -1, True )
        d_tup_lst = get_bases_lst( a_lst, M, d_lst, m1_lst, True )
        print( d_tup_lst )
        assert str( d_tup_lst ) == '[(e0-e1, e0-e2, e3, e0-e1-e2), (e0-e1, e0-e2, e0-e1-e2, e3)]'

        for d_tup in d_tup_lst:
            B = sage_matrix( sage_ZZ, [ d.e_lst for d in d_tup ] )
            dplB = dpl.get_basis_change( B )
            int_mat = list( dplB.m1_lst[0].int_mat )
            print( str( int_mat ) )
            assert str( int_mat ) == '[(0, 1, 0, 0), (1, 0, 0, 0), (0, 0, -1, 0), (0, 0, 0, -1)]'

            # print( list( B ) )
            # print( dplB )

        NSTools.set_enable_tool_dct( True )


    def test__get_webs__rank_4( self ):
        NSTools.set_enable_tool_dct( False )

        # sage_register_unpickle_override( 'class_div', 'Div', Div )
        # sage_register_unpickle_override( 'class_dp_lattice', 'DPLattice', DPLattice )

        d_lst = []
        Md_lst = []
        M = sage_identity_matrix( 4 )
        dpl = DPLattice( d_lst, Md_lst, M )
        fam_lst_lst = get_webs( dpl )
        for fam_lst in fam_lst_lst:
            print( fam_lst )

        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    # NSTools.filter( 'ns_basis.py' )
    NSTools.filter( None )

    # TestNSBasis().test__get_basis_lst__rank_4__False()
    # TestNSBasis().test__get_basis_lst__rank_4__True()
    TestNSBasis().test__get_webs__rank_4()

