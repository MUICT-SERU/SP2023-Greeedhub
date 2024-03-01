'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 13, 2017
@author: Niels Lubbes
'''
from sage.all import *
from ns_lattice.dp_root_bases import *


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
        test_G = Graph()
        test_G.add_vertices( [0, 1, 2] )
        test_G.add_edge( 0, 1, 1 )
        test_G.add_edge( 1, 2, 1 )
        assert G == test_G


    def test__get_ext_graph( self ):
        pass


    def test__get_dynkin_type( self ):
        NSTools.set_enable_tool_dct( False )
        bas_lst = [12, 23, 34 ]
        d_lst = [Div.new( str( bas ), 5 ) for bas in bas_lst]
        print d_lst
        assert get_dynkin_type( d_lst ) == 'A3'
        NSTools.set_enable_tool_dct( True )


    def test__get_orthogonal_roots( self ):
        pass


    def test__get_subspace_roots( self ):
        pass


    def test__is_equal_root_lst( self ):
        pass


    def test__get_root_bases_3( self ):
        NSTools.set_enable_tool_dct( False )
        d_lst_lst = get_root_bases( 3 )
        print d_lst_lst
        assert str( d_lst_lst ) == '[[], [e1-e2], [-e1+e2]]'
        NSTools.set_enable_tool_dct( True )


    def test__get_root_bases_4( self ):
        NSTools.set_enable_tool_dct( False )
        chk_chk_lst = [ ['e1-e2', 'h-e1-e2-e3'],
                        ['e2-e3', 'h-e1-e2-e3'],
                        ['e1-e3', 'h-e1-e2-e3'],
                        [],
                        ['e1-e2'],
                        ['e2-e3'],
                        ['e1-e3'],
                        ['h-e1-e2-e3'],
                        ['e1-e2', 'e2-e3', 'h-e1-e2-e3'],
                        ['e1-e2', 'e2-e3']]
        d_lst_lst = get_root_bases( 4, True )
        print d_lst_lst
        assert d_lst_lst == [ [Div.new( chk, 4 ) for chk in chk_lst ] for chk_lst in chk_chk_lst ]
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases_3( self ):
        NSTools.set_enable_tool_dct( False )
        dct = get_cls_root_bases( 3 )
        print dct
        assert str( dct[3] ) == '[[], [e1-e2]]'
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases_4( self ):
        NSTools.set_enable_tool_dct( False )
        chk_chk_lst = [ [],
                        ['e1-e2'],
                        ['h-e1-e2-e3'],
                        ['e1-e2', 'e2-e3'],
                        ['e1-e2', 'h-e1-e2-e3'],
                        ['e1-e2', 'e2-e3', 'h-e1-e2-e3'] ]
        dct = get_cls_root_bases( 4 )
        print dct
        assert dct[3] == [[], [Div.new( 'e1-e2', 3 )]]
        assert dct[4] == [ [Div.new( chk, 4 ) for chk in chk_lst ] for chk_lst in chk_chk_lst ]
        NSTools.set_enable_tool_dct( True )


