'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 6, 2017
@author: Niels Lubbes
'''
from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries
from linear_series.get_linear_series import get_mon_lst
from class_test_tools import TestTools


class TestGetLinearSeries( TestTools ):


    def test__get_mon_lst__2_xyz( self ):
        mon_lst = get_mon_lst( 2, PolyRing( 'x,y,z' ).gens() )
        assert str( mon_lst ) == '[x^2, x*y, x*z, y^2, y*z, z^2]'


    def test__get_mon_lst__1_xyvw( self ):
        mon_lst = get_mon_lst( 1, PolyRing( 'x,y,v,w' ).gens() )
        assert str( mon_lst ) == '[x*v, x*w, y*v, y*w]'


    def test__get_mon_lst__2_xyvw( self ):
        mon_lst = get_mon_lst( 2, PolyRing( 'x,y,v,w' ).gens() )
        assert str( mon_lst ) == '[x^2*v^2, x^2*v*w, x^2*w^2, x*y*v^2, x*y*v*w, x*y*w^2, y^2*v^2, y^2*v*w, y^2*w^2]'


    def test__get_linear_series__1( self ):

        # Example from phd thesis of Niels Lubbes (page 159).
        PolyRing.reset_base_field()
        bp_tree = BasePointTree()
        bp = bp_tree.add( 'z', ( 0, 0 ), 1 )
        bp = bp.add( 't', ( 0, 0 ), 1 )
        bp = bp.add( 't', ( -1, 0 ), 1 )
        bp = bp.add( 't', ( 0, 0 ), 1 )

        ls = LinearSeries.get( 2, bp_tree )

        assert str( ls ) == '{ 2, <<x^2, y^2 + x*z>>, QQ[x, y, z] }'


    def test__get_linear_series__2( self ):

        ring = PolyRing( 'x,y,z', True )
        ls = LinearSeries( ['x^2+y^2', 'y^2+x*z'], ring )
        bp_tree_1 = ls.get_bp_tree()

        ls = LinearSeries.get( 2, bp_tree_1 )
        bp_tree_2 = ls.get_bp_tree()

        assert self.equal_output_strings( str( bp_tree_1 ), str( bp_tree_2 ) )


    def test__get_linear_series__3( self ):

        PolyRing.reset_base_field()
        bp_tree_1 = BasePointTree()
        bp_tree_1.add( 'z', ( 0, 0 ), 2 ).add( 't', ( 1, 0 ), 1 )
        bp_tree_1.add( 'z', ( 2, 3 ), 1 )

        bp_tree_2 = LinearSeries.get( 3, bp_tree_1 ).get_bp_tree()

        assert self.equal_output_strings( bp_tree_1.alt_str(), bp_tree_2.alt_str() )


    def test__get_linear_series__4( self ):

        ring = PolyRing( 'x,y,v,w', True )
        ring.ext_num_field( 't^2 + 1' )
        a0 = ring.root_gens()[0]

        bp_tree_1 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
        bp = bp_tree_1.add( 'xv', ( a0, -a0 ), 1 )
        bp = bp_tree_1.add( 'xv', ( -a0, a0 ), 1 )

        bp_tree_2 = LinearSeries.get( 2, bp_tree_1 ).get_bp_tree()

        bp_tree_2_str = bp_tree_2.alt_str()
        bp_tree_2_str = bp_tree_2_str.replace( '(a0)', 'a0' )
        bp_tree_2_str = bp_tree_2_str.replace( '(-a0)', '-a0' )

        assert self.equal_output_strings( bp_tree_1.alt_str(), bp_tree_2_str )


    def test__get_linear_series__5( self ):

        ring = PolyRing( 'x,y,v,w', True )
        ring.ext_num_field( 't^2 + 1' )
        a0 = ring.root_gens()[0]

        bp_tree_1 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
        bp = bp_tree_1.add( 'xv', ( a0, -a0 ), 1 )

        bp_tree_2 = LinearSeries.get( 2, bp_tree_1 ).get_bp_tree()

        bp_tree_2_str = bp_tree_2.alt_str()
        bp_tree_2_str = bp_tree_2_str.replace( '(a0)', 'a0' )
        bp_tree_2_str = bp_tree_2_str.replace( '(-a0)', '-a0' )

        assert self.equal_output_strings( bp_tree_1.alt_str(), bp_tree_2_str )


    def test__get_linear_series__6( self ):

        ring = PolyRing( 'x,y,v,w', True )
        ring.ext_num_field( 't^2 + 1' )
        a0 = ring.root_gens()[0]

        bp_tree_1 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
        bp = bp_tree_1.add( 'xv', ( a0, -a0 ), 2 )

        bp_tree_2 = LinearSeries.get( 2, bp_tree_1 ).get_bp_tree()
        bp_tree_2_str = bp_tree_2.alt_str()
        bp_tree_2_str = bp_tree_2_str.replace( '(a0)', 'a0' )
        bp_tree_2_str = bp_tree_2_str.replace( '(-a0)', '-a0' )

        assert self.equal_output_strings( bp_tree_1.alt_str(), bp_tree_2_str )


    def test__get_linear_series__7( self ):

        ring = PolyRing( 'x,y,z', True )

        # checks that 2 infinitly near base points and
        # a simple base point is not collinear.
        #
        bp_tree = BasePointTree()
        bp_tree.add( 'z', ( 1, 0 ), 1 )
        bp = bp_tree.add( 'z', ( 0, 1 ), 1 )
        bp.add( 't', ( 1, 0 ), 1 )
        ls = LinearSeries.get( 1, bp_tree )

        assert ls.pol_lst == []


if __name__ == '__main__':

    # from linear_series.class_ls_tools import LSTools
    # LSTools.filter( None )
    # LSTools.filter( 'class_linear_series.py' )
    # LSTools.filter( 'test_get_linear_series.py' )
    # TestGetLinearSeries().test__get_mon_lst__2_xyz()
    # TestGetLinearSeries().test__get_mon_lst__1_xyvw()
    # TestGetLinearSeries().test__get_mon_lst__2_xyvw()
    # TestGetLinearSeries().test__get_linear_series__1()
    # TestGetLinearSeries().test__get_linear_series__2()
    # TestGetLinearSeries().test__get_linear_series__3()
    # TestGetLinearSeries().test__get_linear_series__4()
    # TestGetLinearSeries().test__get_linear_series__5()
    # TestGetLinearSeries().test__get_linear_series__6()
    TestGetLinearSeries().test__get_linear_series__7()
    pass
