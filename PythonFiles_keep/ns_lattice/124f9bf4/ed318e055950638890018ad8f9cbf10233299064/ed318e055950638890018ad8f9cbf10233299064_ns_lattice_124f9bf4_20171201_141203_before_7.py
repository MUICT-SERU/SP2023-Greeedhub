'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes


'''
from ns_lattice.class_ns_tools import NSTools
from ns_lattice.class_div import Div
from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_indecomp_divs
from ns_lattice.div_in_lattice import get_ak

class TestDivInLattice:

    def test__get_divs_2_2( self ):

        NSTools.set_enable_tool_dct( False )
        d = Div.new( '2e0-e1-e2' )
        dc = 2
        cc = 2
        c_lst = get_divs( d, dc, cc, True )
        assert [c.get_label() for c in c_lst ] == [ '2e0-e1-e2' ]
        NSTools.set_enable_tool_dct( True )


    def test__get_divs__minus_1_classes__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e1', 'e0-e1-e2']
        out_lst = []
        for div in get_divs( get_ak( 4 ), 1, -1, False ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_divs__minus_1_classes__rank_5( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e1', 'e2', 'e3', 'e4',
                   'e0-e1-e2', 'e0-e1-e3', 'e0-e2-e3',
                   'e0-e1-e4', 'e0-e2-e4', 'e0-e3-e4']
        out_lst = []
        for div in get_divs( get_ak( 5 ), 1, -1, True ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_divs__minus_1_classes__rank_9( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = [ 'e1',
                    'e0-e1-e2',
                    '2e0-e1-e2-e3-e4-e5',
                    '3e0-2e1-e2-e3-e4-e5-e6-e7',
                    '4e0-2e1-2e2-2e3-e4-e5-e6-e7-e8',
                    '5e0-2e1-2e2-2e3-2e4-2e5-2e6-e7-e8',
                    '6e0-3e1-2e2-2e3-2e4-2e5-2e6-2e7-2e8' ]
        out_lst = []
        for div in get_divs( get_ak( 9 ), 1, -1, False ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_divs__minus_2_classes__rank_5__perm_true( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = [12, 23, 13, 34, 24, 14,
                   1123, 1124, 1134, 1234]
        out_lst = []
        for div in get_divs( get_ak( 5 ), 0, -2, True ):
            out_lst += [ int( div.get_label( True ) ) ]
        print( out_lst )
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_divs__fam_classes__rank_6__perm_false( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e0-e1', '2e0-e1-e2-e3-e4']
        out_lst = []
        for div in get_divs( get_ak( 6 ), 2, 0, False ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_divs__fam_classes__rank_6__perm_true( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e0-e1', 'e0-e2', 'e0-e3',
                   'e0-e4', 'e0-e5',
                   '2e0-e1-e2-e3-e4',
                   '2e0-e1-e2-e3-e5',
                   '2e0-e1-e2-e4-e5',
                   '2e0-e1-e3-e4-e5',
                   '2e0-e2-e3-e4-e5']

        out_lst = []
        for div in get_divs( get_ak( 6 ), 2, 0, True ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_indecomp_divs( self ):
        NSTools.set_enable_tool_dct( False )
        c_lst = ['e0-e1', 'e0-e2', 'e0-e3',
                 'e0-e4', 'e0-e5',
                 '2e0-e1-e2-e3-e4',
                 '2e0-e1-e2-e3-e5',
                 '2e0-e1-e2-e4-e5',
                 '2e0-e1-e3-e4-e5',
                 '2e0-e2-e3-e4-e5']
        c_lst = [ Div.new( c ) for c in c_lst ]

        d_lst = [ 12, 1123 ]
        d_lst = [ Div.new( str( d ) ) for d in d_lst ]

        chk_lst = ['e0-e1', 'e0-e3', 'e0-e4', 'e0-e5',
                   '2e0-e1-e2-e4-e5', '2e0-e1-e3-e4-e5']

        out_lst = []
        for div in get_indecomp_divs( c_lst, d_lst ):
            out_lst += [ div.get_label() ]
        print( out_lst )
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    NSTools.filter( None )

    TestDivInLattice().test__get_divs__minus_2_classes__rank_5__perm_true()
