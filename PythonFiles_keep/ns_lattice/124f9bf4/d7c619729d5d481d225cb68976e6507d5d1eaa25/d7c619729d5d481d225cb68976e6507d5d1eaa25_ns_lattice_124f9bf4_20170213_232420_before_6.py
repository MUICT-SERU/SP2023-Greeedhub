'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes
'''
from sage.all import *

from ns_lattice.div_set import *

class TestDivSet:

    def test__get_div_set__3p4tm1_1_m1( self ):
        chk_lst = ['h-e1-e2', 'h-e1-e3', 'h-e1-e4', 'h-e2-e3', 'h-e2-e4', 'h-e3-e4']
        out_lst = []

        d = Div( [3] + 4 * [-1] )
        for div in get_div_set( d, 1, -1, True ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst


    def test__get_div_set__3p8tm1_1_m1( self ):
        chk_lst = [ '6h-3e1-2e2-2e3-2e4-2e5-2e6-2e7-2e8',
                    '5h-2e1-2e2-2e3-2e4-2e5-2e6-e7-e8',
                    '4h-2e1-2e2-2e3-e4-e5-e6-e7-e8',
                    '3h-2e1-e2-e3-e4-e5-e6-e7',
                    '2h-e1-e2-e3-e4-e5',
                    'h-e1-e2']
        out_lst = []

        d = Div( [3] + 8 * [-1] )
        for div in get_div_set( d, 1, -1, False ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst


    def test__get_m1_classes__3_True( self ):
        chk_lst = ['h-e1-e2', 'e1', 'e2']
        out_lst = []

        for div in get_m1_classes( 3, True, [] ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst


    def test__get_m1_classes__4_True( self ):
        chk_lst = ['h-e1-e2', 'h-e1-e3', 'h-e2-e3', 'e1', 'e2', 'e3' ]
        out_lst = []

        for div in get_m1_classes( 4, True, [] ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst


    def test__get_m1_classes__5_True( self ):
        chk_lst = ['h-e1-e2', 'h-e1-e3', 'h-e1-e4', 'h-e2-e3', 'h-e2-e4', 'h-e3-e4', 'e1', 'e2', 'e3', 'e4']
        out_lst = []

        for div in get_m1_classes( 5, True, [] ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst


    def test__get_m1_classes__9_False( self ):
        chk_lst = [ '6h-3e1-2e2-2e3-2e4-2e5-2e6-2e7-2e8',
                    '5h-2e1-2e2-2e3-2e4-2e5-2e6-e7-e8',
                    '4h-2e1-2e2-2e3-e4-e5-e6-e7-e8',
                    '3h-2e1-e2-e3-e4-e5-e6-e7',
                    '2h-e1-e2-e3-e4-e5',
                    'h-e1-e2',
                    'e1']
        out_lst = []

        for div in get_m1_classes( 9, False, [] ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst


    def test__get_m2_classes__5_True( self ):

        chk_lst = [1123, 1124, 1134, 1234, 12, 13, 14, 23, 24, 34]
        out_lst = []

        m2_lst = get_m2_classes( 5, True )
        m2_lst.sort( reverse = True )
        for div in m2_lst:
            out_lst += [ int( div.get_label( True ) ) ]

        print out_lst
        assert out_lst == chk_lst


    def test__get_fam_classes__6_False( self ):
        chk_lst = ['2h-e1-e2-e3-e4', 'h-e1']
        out_lst = []
        for div in get_fam_classes( 6, False, [] ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst


    def test__get_fam_classes__6_True( self ):
        chk_lst = ['2h-e1-e2-e3-e4',
                   '2h-e1-e2-e3-e5',
                   '2h-e1-e2-e4-e5',
                   '2h-e1-e3-e4-e5',
                   '2h-e2-e3-e4-e5',
                   'h-e1',
                   'h-e2',
                   'h-e3',
                   'h-e4',
                   'h-e5' ]
        out_lst = []
        for div in get_fam_classes( 6, True, [] ):
            out_lst += [ div.get_label() ]
        assert out_lst == chk_lst



