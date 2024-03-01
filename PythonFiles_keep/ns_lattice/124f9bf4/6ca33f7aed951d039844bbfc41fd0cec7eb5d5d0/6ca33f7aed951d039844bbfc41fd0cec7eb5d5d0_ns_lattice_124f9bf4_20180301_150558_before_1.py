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
from ns_lattice.ns_basis import contains_perm
from ns_lattice.ns_basis import triples


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


    def test__contains_perm__rank6( self ):

        f_lst_lst = [['e0-e1', '2e0-e2-e3-e4-e5'], ['e0-e5', 'e0', 'e1']]
        c_lst = ['e0-e2', '2e0-e1-e3-e4-e5']
        rank = 6

        nf_lst_lst = []
        for f_lst in f_lst_lst:
            nf_lst_lst += [[ Div.new( f, rank ) for f in f_lst ]]
        f_lst_lst = nf_lst_lst
        c_lst = [ Div.new( c, rank ) for c in c_lst ]

        assert contains_perm( f_lst_lst, c_lst )


    def test__triples( self ):
        NSTools.set_enable_tool_dct( False )

        rank = 6

        # (2A1, 4A1)
        d_lst = [ 'e2-e4', 'e3-e5', 'e0-e1-e2-e4', 'e0-e1-e3-e5']
        Md_lst = ['e4-e5', 'e0-e1-e2-e3']
        M = [( 2, 1, 1, 1, 0, 0 ), ( -1, 0, -1, -1, 0, 0 ), ( -1, -1, 0, -1, 0, 0 ), ( -1, -1, -1, 0, 0, 0 ), ( 0, 0, 0, 0, 0, 1 ), ( 0, 0, 0, 0, 1, 0 )]

        d_lst = [ Div.new( d, rank ) for d in d_lst ]
        Md_lst = [ Div.new( Md, rank ) for Md in Md_lst ]
        M = sage_matrix( M )

        dpl = DPLattice( d_lst, Md_lst, M )

        t_lst = triples( dpl, 2 )
        print( t_lst )

        assert str( t_lst ) == '[[e0-e1, e0-e2, 2e0-e2-e3-e4-e5]]'

        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    # NSTools.filter( 'ns_basis.py' )
    NSTools.filter( None )

    # TestNSBasis().test__get_basis_lst__rank_4__False()
    # TestNSBasis().test__get_basis_lst__rank_4__True()
    # TestNSBasis().test__get_webs__rank_4()
    # TestNSBasis().test__contains_perm__rank6()
    TestNSBasis().test__triples()

    pass

