'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes
'''
from sage.all import *

from ns_lattice.div_set import *

class TestDivSet:

    def test__get_div_set__3p4tm1_1_m1( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e0-e1-e2', 'e0-e1-e3', 'e0-e2-e3', 'e0-e1-e4', 'e0-e2-e4', 'e0-e3-e4']
        out_lst = []
        d = Div( [3] + 4 * [-1] )
        for div in get_div_set( d, 1, -1, True ):
            out_lst += [ div.get_label() ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_div_set__3p8tm1_1_m1( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = [ 'e0-e1-e2',
                    '2e0-e1-e2-e3-e4-e5',
                    '3e0-2e1-e2-e3-e4-e5-e6-e7',
                    '4e0-2e1-2e2-2e3-e4-e5-e6-e7-e8',
                    '5e0-2e1-2e2-2e3-2e4-2e5-2e6-e7-e8',
                    '6e0-3e1-2e2-2e3-2e4-2e5-2e6-2e7-2e8' ]
        out_lst = []
        d = Div( [3] + 8 * [-1] )
        for div in get_div_set( d, 1, -1, False ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_m1_classes__3_True( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e2', 'e1', 'e0-e1-e2']
        out_lst = []
        for div in get_m1_classes( 3, True, [] ):
            out_lst += [ div.get_label() ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_m1_classes__4_True( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e3', 'e2', 'e1', 'e0-e1-e2', 'e0-e1-e3', 'e0-e2-e3']
        out_lst = []
        for div in get_m1_classes( 4, True, [] ):
            out_lst += [ div.get_label() ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_m1_classes__5_True( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e4', 'e3', 'e2', 'e1', 'e0-e1-e2', 'e0-e1-e3',
                   'e0-e2-e3', 'e0-e1-e4', 'e0-e2-e4', 'e0-e3-e4']
        out_lst = []
        for div in get_m1_classes( 5, True, [] ):
            out_lst += [ div.get_label() ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_m1_classes__9_False( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = [ 'e1',
                    'e0-e1-e2',
                    '2e0-e1-e2-e3-e4-e5',
                    '3e0-2e1-e2-e3-e4-e5-e6-e7',
                    '4e0-2e1-2e2-2e3-e4-e5-e6-e7-e8',
                    '5e0-2e1-2e2-2e3-2e4-2e5-2e6-e7-e8',
                    '6e0-3e1-2e2-2e3-2e4-2e5-2e6-2e7-2e8' ]
        out_lst = []
        for div in get_m1_classes( 9, False, [] ):
            out_lst += [ div.get_label() ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_m2_classes__5_True( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = [12, 23, 13, 34, 24, 14, 1123, 1124, 1134, 1234]
        out_lst = []
        m2_lst = get_m2_classes( 5, True )
        for div in m2_lst:
            out_lst += [ int( div.get_label( True ) ) ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_fam_classes__6_False( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e0-e1', '2e0-e1-e2-e3-e4']
        out_lst = []
        for div in get_fam_classes( 6, False, [] ):
            out_lst += [ div.get_label() ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )


    def test__get_fam_classes__6_True( self ):
        NSTools.set_enable_tool_dct( False )
        chk_lst = ['e0-e1', 'e0-e2', 'e0-e3',
                   'e0-e4', 'e0-e5',
                   '2e0-e1-e2-e3-e4',
                   '2e0-e1-e2-e3-e5',
                   '2e0-e1-e2-e4-e5',
                   '2e0-e1-e3-e4-e5',
                   '2e0-e2-e3-e4-e5']

        out_lst = []
        for div in get_fam_classes( 6, True, [] ):
            out_lst += [ div.get_label() ]
        print out_lst
        assert out_lst == chk_lst
        NSTools.set_enable_tool_dct( True )
