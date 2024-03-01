'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes
'''
from nose import with_setup  # optional

from ns_lattice import *

class TestClassDiv:


    def test__new( self ):
        assert Div.new( '3h+e1+5e5-e6' ).e_lst == [3, 1, 0, 0, 0, 5, -1, 0, 0]
        assert Div.new( 'e1-e2' ).e_lst == [0, 1, -1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-e1+e2' ).e_lst == [0, -1, 1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-3h' ).e_lst == [-3, 0, 0, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-e3' ).e_lst == [0, 0, 0, -1, 0, 0, 0, 0, 0]
        assert Div.new( '12' ).e_lst == [0, 1, -1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-12' ).e_lst == [0, -1, 1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '1245' ).e_lst == [1, 0, -1, 0, -1, -1, 0, 0, 0]
        assert Div.new( '214' ).e_lst == [2, 0, -1, -1, 0, -1, -1, -1, -1]
        assert Div.new( '306' ).e_lst == [3, -1, -1, -1, -1, -1, -2, -1, -1]
        assert Div.new( '-308' ).e_lst == [-3, 1, 1, 1, 1, 1, 1, 1, 2]


    def test__get_label__False( self ):
        assert Div( [3, 1, 0, 0, 0, 5, -1, 0, 0] ).get_label( False ) == '3h+e1+5e5-e6'
        assert Div( [0, 1, -1, 0, 0, 0, 0, 0, 0] ).get_label( False ) == '12'
        assert Div( [0, -1, 1, 0, 0, 0, 0, 0, 0] ).get_label( False ) == '-12'
        assert Div( [-3, 0, 0, 0, 0, 0, 0, 0, 0] ).get_label( False ) == '-3h'
        assert Div( [0, 0, 0, -1, 0, 0, 0, 0, 0] ).get_label( False ) == '-e3'
        assert Div( [0, 1, -1, 0, 0, 0, 0, 0, 0] ).get_label( False ) == '12'
        assert Div( [0, -1, 1, 0, 0, 0, 0, 0, 0] ).get_label( False ) == '-12'
        assert Div( [1, 0, -1, 0, -1, -1, 0, 0, 0] ).get_label( False ) == '1245'
        assert Div( [2, 0, -1, -1, 0, -1, -1, -1, -1] ).get_label( False ) == '214'
        assert Div( [3, -1, -1, -1, -1, -1, -2, -1, -1] ).get_label( False ) == '306'
        assert Div( [-3, 1, 1, 1, 1, 1, 1, 1, 2] ).get_label( False ) == '-308'


    def test__get_label__True( self ):
        assert Div.new( 'e1' ).get_label( True ) == 'e1'
        assert Div.new( 'e1-e2' ).get_label( True ) == 'e12'
        assert Div.new( '2h-e1-e2-e4-e5' ).get_label( True ) == '2e1245'
        assert Div.new( 'h-e1' ).get_label( True ) == '1e1'


    def test__lt( self ):
        assert Div.new( '1124' ) < Div.new( '1123' )
        assert Div.new( '12' ) < Div.new( '1123' )
        assert Div.new( '13' ) < Div.new( '12' )
        assert Div.new( '34' ) < Div.new( '12' )





