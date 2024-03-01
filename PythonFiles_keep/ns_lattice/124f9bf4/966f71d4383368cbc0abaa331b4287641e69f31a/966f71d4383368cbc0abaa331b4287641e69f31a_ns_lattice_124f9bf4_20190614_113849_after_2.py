'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_matrix

from ns_lattice.class_div import Div

from ns_lattice.class_ns_tools import NSTools


class TestClassDiv:


    def test__new( self ):
        assert Div.new( '3e0+e1+5e5-e6' ).e_lst == [3, 1, 0, 0, 0, 5, -1, 0, 0]
        assert Div.new( 'e1-e2' ).e_lst == [0, 1, -1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-e1+e2' ).e_lst == [0, -1, 1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-3e0' ).e_lst == [-3, 0, 0, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-e3' ).e_lst == [0, 0, 0, -1, 0, 0, 0, 0, 0]
        assert Div.new( '12' ).e_lst == [0, 1, -1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '-12' ).e_lst == [0, -1, 1, 0, 0, 0, 0, 0, 0]
        assert Div.new( '1245' ).e_lst == [1, 0, -1, 0, -1, -1, 0, 0, 0]
        assert Div.new( '214' ).e_lst == [2, 0, -1, -1, 0, -1, -1, -1, -1]
        assert Div.new( '306' ).e_lst == [3, -1, -1, -1, -1, -1, -2, -1, -1]
        assert Div.new( '-308' ).e_lst == [-3, 1, 1, 1, 1, 1, 1, 1, 2]


    def test__get_label__True( self ):
        assert Div( [3, 1, 0, 0, 0, 5, -1, 0, 0] ).get_label( True ) == '3e0+e1+5e5-e6'
        assert Div( [0, 1, -1, 0, 0, 0, 0, 0, 0] ).get_label( True ) == '12'
        assert Div( [0, -1, 1, 0, 0, 0, 0, 0, 0] ).get_label( True ) == '-12'
        assert Div( [-3, 0, 0, 0, 0, 0, 0, 0, 0] ).get_label( True ) == '-3e0'
        assert Div( [0, 0, 0, -1, 0, 0, 0, 0, 0] ).get_label( True ) == '-e3'
        assert Div( [0, 1, -1, 0, 0, 0, 0, 0, 0] ).get_label( True ) == '12'
        assert Div( [0, -1, 1, 0, 0, 0, 0, 0, 0] ).get_label( True ) == '-12'
        assert Div( [1, 0, -1, 0, -1, -1, 0, 0, 0] ).get_label( True ) == '1245'
        assert Div( [2, 0, -1, -1, 0, -1, -1, -1, -1] ).get_label( True ) == '214'
        assert Div( [3, -1, -1, -1, -1, -1, -2, -1, -1] ).get_label( True ) == '306'
        assert Div( [-3, 1, 1, 1, 1, 1, 1, 1, 2] ).get_label( True ) == '-308'


    def test__get_abbr_label( self ):
        assert Div.new( 'e1' ).get_abbr_label() == 'e1'
        assert Div.new( 'e1-e2' ).get_abbr_label() == 'e12'
        assert Div.new( '2e0-e1-e2-e4-e5' ).get_abbr_label() == '2e1245'
        assert Div.new( 'e0-e1' ).get_abbr_label() == '1e1'


    def test__lt( self ):
        assert Div.new( '1123' ) < Div.new( '1124' )
        assert Div.new( '12' ) < Div.new( '1123' )
        assert Div.new( '12' ) < Div.new( '13' )
        assert Div.new( '12' ) < Div.new( '34' )


    def test__get_basis_change( self ):

        B = sage_matrix( sage_ZZ, [( 1, -1, 0, 0, 0, 0 ),
                                   ( 1, 0, -1, 0, 0, 0 ),
                                   ( 1, -1, -1, 0, 0, 0 ),
                                   ( 0, 0, 0, 1, 0, 0 ),
                                   ( 0, 0, 0, 0, 1, 0 ),
                                   ( 0, 0, 0, 0, 0, 1 )] )

        # (-2)-classes
        assert Div.new( '1123', 6 ).get_basis_change( B ).get_label() == 'e2-e3'
        assert Div.new( '1345', 6 ).get_basis_change( B ).get_label() == 'e0+e1-e2-e3-e4-e5'
        assert Div.new( '12', 6 ).get_basis_change( B ).get_label() == '-e0+e1'
        assert Div.new( '13', 6 ).get_basis_change( B ).get_label() == 'e1-e2-e3'
        assert Div.new( '23', 6 ).get_basis_change( B ).get_label() == 'e0-e2-e3'

        # (-1)-classes
        assert Div.new( 'e1', 6 ).get_basis_change( B ).get_label() == 'e1-e2'
        assert Div.new( 'e2', 6 ).get_basis_change( B ).get_label() == 'e0-e2'
        assert Div.new( 'e3', 6 ).get_basis_change( B ).get_label() == 'e3'
        assert Div.new( '2e0-e1-e2-e3-e4-e5', 6 ).get_basis_change( B ).get_label() == 'e0+e1-e3-e4-e5'

        # classes of conical families
        assert Div.new( 'e0-e1', 6 ).get_basis_change( B ).get_label() == 'e0'
        assert Div.new( 'e0-e2', 6 ).get_basis_change( B ).get_label() == 'e1'
        assert Div.new( 'e0-e3', 6 ).get_basis_change( B ).get_label() == 'e0+e1-e2-e3'
        assert Div.new( '2e0-e1-e3-e4-e5', 6 ).get_basis_change( B ).get_label() == '2e0+e1-e2-e3-e4-e5'
        assert Div.new( '2e0-e2-e3-e4-e5', 6 ).get_basis_change( B ).get_label() == 'e0+2e1-e2-e3-e4-e5'


    def test__is_positive( self ):
        assert Div.new( 'e0-e1', 6 ).is_positive()
        assert Div.new( 'e1-e2', 6 ).is_positive()
        assert not Div.new( '-e2+e1', 6 ).is_positive()
        assert not Div.new( '-e0+e1+e2', 6 ).is_positive()


if __name__ == '__main__':

    NSTools.filter( None )


    TestClassDiv().test__is_positive()

    pass






