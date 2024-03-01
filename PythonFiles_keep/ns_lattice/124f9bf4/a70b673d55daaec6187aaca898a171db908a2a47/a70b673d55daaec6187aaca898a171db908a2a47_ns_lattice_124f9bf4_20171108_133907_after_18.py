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
from ns_lattice.dp_root_bases import get_ext_graph
from ns_lattice.dp_root_bases import get_dynkin_type
from ns_lattice.dp_root_bases import get_root_bases
from ns_lattice.dp_root_bases import get_cls_root_bases
from ns_lattice.dp_root_bases import is_equal_root_bases
from ns_lattice.dp_root_bases import get_graph


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


    def test__is_equal_root_bases( self ):
        assert is_equal_root_bases( [Div.new( '23', 4 )], [Div.new( '1123', 4 )] ) == False
        assert is_equal_root_bases( [Div.new( '23', 4 )], [Div.new( '12', 4 )] ) == True


    def test__get_dynkin_type( self ):
        NSTools.set_enable_tool_dct( False )
        bas_lst = [12, 23, 34 ]
        d_lst = [Div.new( str( bas ), 5 ) for bas in bas_lst]
        print( d_lst )
        assert get_dynkin_type( d_lst ) == 'A3'
        NSTools.set_enable_tool_dct( True )


    def test__get_root_bases__rank_3__pos_false( self ):
        NSTools.set_enable_tool_dct( False )
        d_lst_lst = get_root_bases( 3, False )
        print( d_lst_lst )
        assert str( d_lst_lst ) == '[[], [e1-e2], [-e1+e2]]'
        NSTools.set_enable_tool_dct( True )


    def test__get_root_bases__rank_3__pos_true( self ):
        NSTools.set_enable_tool_dct( False )
        d_lst_lst = get_root_bases( 3, True )
        print( d_lst_lst )
        assert str( d_lst_lst ) == '[[], [e1-e2]]'
        NSTools.set_enable_tool_dct( True )


    def test__get_root_bases__rank_4__pos_true__fast_true( self ):
        NSTools.set_enable_tool_dct( False )
        chk_chk_lst = [ ['e1-e2', 'e0-e1-e2-e3'],
                        ['e1-e3', 'e0-e1-e2-e3'],
                        ['e2-e3', 'e0-e1-e2-e3'],
                        [],
                        ['e1-e2'],
                        ['e1-e3'],
                        ['e2-e3'],
                        ['e0-e1-e2-e3'],
                        ['e1-e2', 'e2-e3', 'e0-e1-e2-e3'],
                        ['e1-e2', 'e2-e3']]
        d_lst_lst = get_root_bases( 4, True, True )
        print( d_lst_lst )
        assert d_lst_lst == [ [Div.new( chk, 4 ) for chk in chk_lst ] for chk_lst in chk_chk_lst ]
        NSTools.set_enable_tool_dct( True )


    def test__get_root_bases__rank_4__pos_true__fast_false( self ):
        NSTools.set_enable_tool_dct( False )
        chk_chk_lst = [ ['e1-e2', 'e0-e1-e2-e3'],
                        ['e2-e3', 'e0-e1-e2-e3'],
                        ['e1-e3', 'e0-e1-e2-e3'],
                        [],
                        ['e1-e2'],
                        ['e2-e3'],
                        ['e1-e3'],
                        ['e0-e1-e2-e3'],
                        ['e1-e2', 'e2-e3', 'e0-e1-e2-e3'],
                        ['e1-e2', 'e2-e3']]
        d_lst_lst = get_root_bases( 4, True, False )
        print( d_lst_lst )
        assert d_lst_lst == [ [Div.new( chk, 4 ) for chk in chk_lst ] for chk_lst in chk_chk_lst ]
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases__rank_3( self ):
        NSTools.set_enable_tool_dct( False )
        dct = get_cls_root_bases( 3 )
        print( dct )
        assert str( dct[3] ) == '[[], [e1-e2]]'
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        chk_chk_lst = [ [],
                        ['e1-e2'],
                        ['e0-e1-e2-e3'],
                        ['e1-e2', 'e2-e3'],
                        ['e1-e2', 'e0-e1-e2-e3'],
                        ['e1-e2', 'e2-e3', 'e0-e1-e2-e3'] ]
        dct = get_cls_root_bases( 4 )
        print( dct )
        assert dct[3] == [[], [Div.new( 'e1-e2', 3 )]]
        assert dct[4] == [ [Div.new( chk, 4 ) for chk in chk_lst ] for chk_lst in chk_chk_lst ]
        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    NSTools.filter( None )

    TestDPRootBasis().test__get_ext_graph()

