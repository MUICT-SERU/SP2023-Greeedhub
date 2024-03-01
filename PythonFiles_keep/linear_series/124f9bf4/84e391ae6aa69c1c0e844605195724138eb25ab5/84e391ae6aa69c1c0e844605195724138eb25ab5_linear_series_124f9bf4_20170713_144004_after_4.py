'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 6, 2017
@author: Niels Lubbes
'''

from linear_series.class_poly_ring import PolyRing
from linear_series.class_linear_series import LinearSeries


class TestClassLinearSeries:


    def test__subs( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + 1' )
        ring.ext_num_field( 't^3 + a0' )

        a0, a1 = ring.root_gens()
        x, y, z = ring.gens()

        pol_lst = [x ** 2 + a0 * y * z, y + a1 * z + x ]
        ls = LinearSeries( pol_lst, ring )
        assert str( ls.pol_lst ) == '[x^2 + a0*y*z, x + y + a1*z]'

        ls.subs( {x: x + 1} )
        assert str( ls.pol_lst ) == '[x^2 + a0*y*z + 2*x + 1, x + y + a1*z + 1]'


    def test__chart( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + 1' )
        ring.ext_num_field( 't^3 + a0' )


        ls = LinearSeries( ['x^2+a0*y*z', 'x+y+a1*z '], ring )
        xls = ls.copy().chart( ['x'] )

        assert str( xls.pol_lst ) == '[a0*y*z + 1, y + a1*z + 1]'


    def test__diff( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + 1' )
        ring.ext_num_field( 't^3 + a0' )

        ls = LinearSeries( ['a0*x^2+y^3*z^3', 'x+z+z^3*y^4'], ring )
        xls = ls.copy().chart( ['x'] )

        assert str( xls.diff( 3, 2 ).pol_lst ) == '[36*z, 144*y*z]'


    def test__translate_to_origin( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + 1' )
        ring.ext_num_field( 't^3 + a0' )

        ls = LinearSeries( ['y^2', 'y*x'], ring )
        xls = ls.copy().chart( ['x'] )

        a0, a1 = ring.coerce( 'a0,a1' )

        xls.translate_to_origin( ( a0 + 1, a1 + a0 ) )
        assert str( xls ) == '{ 2, <<y^2 + (2*a0 + 2)*y + 2*a0, y + a0 + 1>>, QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1> )[y, z] }'


    def test__blow_up_origin( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + 1' )
        ring.ext_num_field( 't^3 + a0' )

        ls = LinearSeries( ['x^2', 'x*z + y^2'], ring )
        zls = ls.copy().chart( ['z'] )

        zls, m = zls.blow_up_origin( 's' )
        assert str( zls ) == '{ 2, <<x, x*y^2 + 1>>, QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1> )[x, y] }'
        assert m == 1

    def test__quo( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + 1' )
        ring.ext_num_field( 't^3 + a0' )

        ls = LinearSeries( ['x^2', 'x + x^2'], ring )
        assert str( ls.quo( 'x' ) ) == '{ 2, <<x, x + 1>>, QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1> )[x, y, z] }'




if __name__ == '__main__':

    # TestClassLinearSeries().test__subs()
    # TestClassLinearSeries().test__chart()
    # TestClassLinearSeries().test__diff()
    # TestClassLinearSeries().test__translate_to_origin()
    # TestClassLinearSeries().test__blow_up_origin()
    # TestClassLinearSeries().test__quo()
    pass
