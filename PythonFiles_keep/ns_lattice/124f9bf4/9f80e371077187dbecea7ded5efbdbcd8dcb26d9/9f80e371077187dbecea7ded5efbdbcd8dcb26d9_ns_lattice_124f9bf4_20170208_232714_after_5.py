'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes
'''
from ns_lattice import *


class TestDPInvolutions():

    def test__complete_basis__34_45_rank6( self ):
        d_lst = [ 34, 45]
        rank = 6
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        mat = complete_basis( d_lst )
        assert mat == matrix( [( 0, 0, -1, 0, 0, 0 ),
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
        assert mat == matrix( [( 0, 0, 0, -1, 0, 0 ),
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
        assert mat == matrix( [( 1, 0, 0, 0, -3, 0 ),
                               ( -1, 1, 0, 0, 1, 0 ),
                               ( -1, -1, 1, 0, 1, 0 ),
                               ( -1, 0, -1, 0, 1, 0 ),
                               ( 0, 0, 0, 1, 0, 1 ),
                               ( 0, 0, 0, -1, 0, 1 ) ] )


    def test__complete_basis__1145_23_rank6( self ):
        d_lst = [ 1145, 23 ]
        rank = 6
        d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
        mat = complete_basis( d_lst )
        assert mat == matrix( [( 1, 0, -1, 0, 0, 0 ),
                               ( -1, 0, 0, 1, 0, 0 ),
                               ( 0, 1, 0, 0, 1, 0 ),
                               ( 0, -1, 0, 0, 1, 0 ),
                               ( -1, 0, 0, 0, 0, 1 ),
                               ( -1, 0, 1, -1, 0, -1 ) ] )




