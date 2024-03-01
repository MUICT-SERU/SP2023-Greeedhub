'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_vector
from ns_lattice.sage_interface import sage_matrix
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_diagonal_matrix

from ns_lattice.dp_involutions import complete_basis
from ns_lattice.dp_involutions import is_integral_involution
from ns_lattice.dp_involutions import basis_to_involution
from ns_lattice.class_div import Div

from ns_lattice.class_ns_tools import NSTools


class TestDPInvolutions():

    def test__complete_basis__34_45_rank6( self ):
        d_lst = [ 34, 45]
        rank = 6
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        mat = complete_basis( d_lst )
        assert mat == sage_matrix( [( 0, 0, -1, 0, 0, 0 ),
                                    ( 0, 0, 0, 1, 0, 0 ),
                                    ( 0, 0, 0, 0, 1, 0 ),
                                    ( 1, 0, 0, 0, 0, 1 ),
                                    ( -1, 1, 0, 0, 0, 1 ),
                                    ( 0, -1, 0, 0, 0, 1 )] )


    def test__complete_basis__23_34_45_rank6( self ):

        d_lst = [ 23, 34, 45 ]
        rank = 6
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        mat = complete_basis( d_lst )
        assert mat == sage_matrix( [( 0, 0, 0, -1, 0, 0 ),
                                    ( 0, 0, 0, 0, 1, 0 ),
                                    ( 1, 0, 0, 0, 0, 1 ),
                                    ( -1, 1, 0, 0, 0, 1 ),
                                    ( 0, -1, 1, 0, 0, 1 ),
                                    ( 0, 0, -1, 0, 0, 1 )] )


    def test__complete_basis__1123_12_23_45_rank6( self ):
        # 4A1
        d_lst = [ 1123, 12, 23, 45 ]
        rank = 6
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        mat = complete_basis( d_lst )
        print( mat )
        assert mat == sage_matrix( [( 0, 0, 0, 1, -3, 0 ),
                                    ( 1, 0, 0, -1, 1, 0 ),
                                    ( -1, 1, 0, -1, 1, 0 ),
                                    ( 0, -1, 0, -1, 1, 0 ),
                                    ( 0, 0, 1, 0, 0, 1 ),
                                    ( 0, 0, -1, 0, 0, 1 ) ] )


    def test__complete_basis__1145_23_rank6( self ):
        d_lst = [ 1145, 23 ]
        rank = 6
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        mat = complete_basis( d_lst )
        print( mat )
        assert mat == sage_matrix( [( 0, 1, -1, 0, 0, 0 ),
                                    ( 0, -1, 0, 1, 0, 0 ),
                                    ( 1, 0, 0, 0, 1, 0 ),
                                    ( -1, 0, 0, 0, 1, 0 ),
                                    ( 0, -1, 0, 0, 0, 1 ),
                                    ( 0, -1, 1, -1, 0, -1 ) ] )


    def test__complete_basis__12_23_rank4( self ):
        d_lst = [ 12, 23 ]
        rank = 4
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        V = complete_basis( d_lst )
        D = sage_diagonal_matrix( [-1, -1, 1, 1] )
        J = sage_diagonal_matrix( [1, -1, -1, -1] )
        M = V * D * ~V
        assert str( list( M ) ) == "[(1, 0, 0, 0), (0, -1/3, 2/3, 2/3), (0, 2/3, -1/3, 2/3), (0, 2/3, 2/3, -1/3)]"
        assert M * M == sage_identity_matrix( 4 )
        assert M.T * J * M == J
        assert is_integral_involution( M ) == False



    def test__complete_basis__1123_12_23_rank4( self ):
        d_lst = [ 1123, 12, 23 ]
        rank = 4
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        V = complete_basis( d_lst )
        D = sage_diagonal_matrix( [-1, -1, -1, 1] )
        J = sage_diagonal_matrix( [1, -1, -1, -1] )
        M = V * D * ~V

        print( ~V * sage_vector( [1, -1, -1, -1] ) )
        print( ~V * sage_vector( [0, 1, 0, -1] ) )
        print( ~V * sage_vector( [0, 0, 1, -1] ) )
        print( V )

        assert M == basis_to_involution( d_lst, rank )
        assert str( list( V ) ) == "[(0, 0, 1, -3), (1, 0, -1, 1), (-1, 1, -1, 1), (0, -1, -1, 1)]"
        assert str( list( ~V ) ) == "[(0, 2/3, -1/3, -1/3), (0, 1/3, 1/3, -2/3), (-1/2, -1/2, -1/2, -1/2), (-1/2, -1/6, -1/6, -1/6)]"
        assert str( list( M ) ) == "[(2, 1, 1, 1), (-1, -4/3, -1/3, -1/3), (-1, -1/3, -4/3, -1/3), (-1, -1/3, -1/3, -4/3)]"
        assert M * M == sage_identity_matrix( 4 )
        assert M.T * J * M == J
        assert is_integral_involution( M ) == False


    def test__complete_basis__12__rank4( self ):
        d_lst = [ 12 ]
        rank = 4
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        V = complete_basis( d_lst )
        D = sage_diagonal_matrix( [-1, 1, 1, 1] )
        J = sage_diagonal_matrix( [1, -1, -1, -1] )
        M = V * D * ~V

        assert M == basis_to_involution( d_lst, rank )
        assert str( list( M ) ) == "[(1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)]"
        assert M * M == sage_identity_matrix( 4 )
        assert M.T * J * M == J
        assert is_integral_involution( M ) == True


    def test__complete_basis__1123__rank4( self ):
        d_lst = [ 1123 ]
        rank = 4
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        V = complete_basis( d_lst )
        D = sage_diagonal_matrix( [-1, 1, 1, 1] )
        J = sage_diagonal_matrix( [1, -1, -1, -1] )
        M = V * D * ~V

        assert M == basis_to_involution( d_lst, rank )
        assert str( list( M ) ) == "[(2, 1, 1, 1), (-1, 0, -1, -1), (-1, -1, 0, -1), (-1, -1, -1, 0)]"
        assert M * M == sage_identity_matrix( 4 )
        assert M.T * J * M == J
        assert is_integral_involution( M ) == True


    def test__complete_basis__1123_12__rank4( self ):
        d_lst = [ 1123, 12 ]
        rank = 4
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        V = complete_basis( d_lst )
        D = sage_diagonal_matrix( [-1, -1, 1, 1] )
        J = sage_diagonal_matrix( [1, -1, -1, -1] )
        M = V * D * ~V

        assert M == basis_to_involution( d_lst, rank )
        assert str( list( M ) ) == "[(2, 1, 1, 1), (-1, -1, 0, -1), (-1, 0, -1, -1), (-1, -1, -1, 0)]"
        assert M * M == sage_identity_matrix( 4 )
        assert M.T * J * M == J
        assert is_integral_involution( M ) == True



if __name__ == '__main__':

    NSTools.filter( None )

    # TestDPInvolutions().test__complete_basis__12_23_rank4()
    TestDPInvolutions().test__complete_basis__1123_12_23_rank4()
    # TestDPInvolutions().test__complete_basis__12__rank4()
    # TestDPInvolutions().test__complete_basis__1123__rank4()
    # TestDPInvolutions().test__complete_basis__1123_12__rank4()
    pass


