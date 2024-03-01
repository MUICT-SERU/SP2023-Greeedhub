'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 13, 2017
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_Graph

from ns_lattice.class_ns_tools import NSTools
from ns_lattice.class_div import Div

from ns_lattice.dp_root_bases import is_root_basis
from ns_lattice.dp_root_bases import get_graph
from ns_lattice.dp_root_bases import get_ext_graph
from ns_lattice.dp_root_bases import get_dynkin_type
from ns_lattice.dp_root_bases import convert_type
from ns_lattice.dp_root_bases import get_root_bases_orbit


class TestDPRootBasis():

    def test__is_root_basis( self ):
        bas_lst = [1123 ]
        assert is_root_basis( [Div.new( str( bas ), 4 ) for bas in bas_lst] )

        bas_lst = [1123, 23 ]
        assert is_root_basis( [Div.new( str( bas ), 4 ) for bas in bas_lst] )

        bas_lst = [1123, 1123 ]
        assert not is_root_basis( [Div.new( str( bas ), 4 ) for bas in bas_lst] )

        bas_lst = [12, -23 ]
        assert not is_root_basis( [Div.new( str( bas ), 4 ) for bas in bas_lst] )


    def test__get_graph( self ):
        bas_lst = [12, 23, 34 ]
        d_lst = [Div.new( str( bas ), 5 ) for bas in bas_lst]
        G = get_graph( d_lst )
        test_G = sage_Graph()
        test_G.add_vertices( [0, 1, 2] )
        test_G.add_edge( 0, 1, 1 )
        test_G.add_edge( 1, 2, 1 )
        assert G == test_G


    def test__get_ext_graph( self ):
        NSTools.set_enable_tool_dct( False )

        #
        # example for Neron-Severi lattice of sextic weak del Pezzo surface
        # The A1 root sub-systems [23] and [1123] are not equivalent.
        # We use as invariant a graph.
        #
        M = sage_identity_matrix( sage_QQ, 4 )  # real structure is the identity
        e_lst = [ 'e1', 'e0-e1-e2', 'e2', 'e0-e2-e3', 'e3', 'e0-e1-e3' ]  # (-1)-classes

        d_lst1 = [Div.new( s, 4 ) for s in e_lst + ['23'] ]
        G1 = get_ext_graph( d_lst1, M )

        d_lst2 = [Div.new( s, 4 ) for s in e_lst + ['1123'] ]
        G2 = get_ext_graph( d_lst2, M )

        assert not G1.is_isomorphic( G2, edge_labels = True )
        NSTools.set_enable_tool_dct( True )


    def test__get_dynkin_type( self ):
        NSTools.set_enable_tool_dct( False )
        bas_lst = [12, 23, 34 ]
        d_lst = [Div.new( str( bas ), 5 ) for bas in bas_lst]
        print( d_lst )
        assert get_dynkin_type( d_lst ) == 'A3'
        NSTools.set_enable_tool_dct( True )


    def test__convert_type( self ):
        NSTools.set_enable_tool_dct( False )

        assert convert_type( '2A1+D4' ) == ['A1', 'A1', 'D4']
        assert convert_type( '2A1+A2+A3' ) == ['A1', 'A1', 'A2', 'A3']
        assert convert_type( 'A0+2A1+3A1+D4+A0' ) == 5 * ['A1'] + ['D4']

        NSTools.set_enable_tool_dct( True )


    def test__get_root_bases_orbit__rank_3( self ):
        NSTools.set_enable_tool_dct( False )

        d_lst = [12]
        d_lst = [Div.new( str( d ), 3 ) for d in d_lst]

        d_lst_lst = get_root_bases_orbit( d_lst, False )
        print( d_lst_lst )
        assert str( d_lst_lst ) == '[[e1-e2], [-e1+e2]]'

        d_lst_lst = get_root_bases_orbit( d_lst, True )
        print( d_lst_lst )
        assert str( d_lst_lst ) == '[[e1-e2]]'

        NSTools.set_enable_tool_dct( True )


    def test__get_root_bases_orbit__rank_4( self ):
        NSTools.set_enable_tool_dct( False )

        d_lst = [12]
        d_lst = [Div.new( str( d ), 4 ) for d in d_lst]

        d_lst_lst = get_root_bases_orbit( d_lst, False )
        print( d_lst_lst )
        assert str( d_lst_lst ) == '[[e1-e2], [-e1+e2], [e1-e3], [-e2+e3], [-e1+e3], [e2-e3]]'

        d_lst_lst = get_root_bases_orbit( d_lst, True )
        print( d_lst_lst )
        assert str( d_lst_lst ) == '[[e1-e2], [e1-e3], [e2-e3]]'

        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    NSTools.filter( None )

    # TestDPRootBasis().test__get_ext_graph()
    # TestDPRootBasis().test__get_root_bases_orbit__rank_3()
    # TestDPRootBasis().test__get_root_bases_orbit__rank_4()
    TestDPRootBasis().test__convert_type()
