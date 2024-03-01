'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 6, 2017
@author: Niels Lubbes
'''
from linear_series.class_poly_ring import PolyRing
from linear_series.class_linear_series import LinearSeries


class TestGetSolutionSet:

    def test__get_solution_set__1( self ):
        ls = LinearSeries( ['x*z^13', 'x*z^13', 'x^9*y^5', 'x^8*y^6', 'x*y*z^12+2*y*z^13'], PolyRing( 'x,y,z', True ) )
        zls = ls.copy().chart( ['z'] )
        print( zls )
        sol_lst = zls.get_solution_set()
        print( sol_lst )


    def test__get_solution_set__2( self ):

        ls = LinearSeries( ['x^2*z+y^2*z', 'y^3+z^3'], PolyRing( 'x,y,z', True ) )
        xls = ls.copy().chart( ['x'] )

        sol_lst = xls.get_solution_set()

        assert str( xls ) == '{ 2, <<y^2*z + z, y^3 + z^3>>, QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1> )[y, z] }'

        assert str( sol_lst ) == '[(-a0, a0), (a0, -a1), (0, 0), (a0, -a0), (a0, a1 + a0), (-a0, a1), (-a0, -a1 - a0)]'

        #
        # ------------------------------
        # Output with Sage solve method:
        # ------------------------------
        #
        # sage: y,z=var('y,z')
        # sage: solve( [y^2*z + z, y^3 + z^3] )
        # out :
        # [
        #  [y == 0,
        #   z == 0],
        #
        #  [y == -1/4*sqrt(2)*(sqrt(I*sqrt(3) + 1) + sqrt(-3*I*sqrt(3) - 3)),
        #   z == -sqrt(1/2*I*sqrt(3) + 1/2)],
        #
        #  [y == 1/4*sqrt(2)*(sqrt(I*sqrt(3) + 1) + sqrt(-3*I*sqrt(3) - 3)),
        #   z == sqrt(1/2*I*sqrt(3) + 1/2)],
        #
        #  [y == -1/4*sqrt(2)*(sqrt(3*I*sqrt(3) - 3) + sqrt(-I*sqrt(3) + 1)),
        #   z == -sqrt(-1/2*I*sqrt(3) + 1/2)],
        #
        #  [y == 1/4*sqrt(2)*(sqrt(3*I*sqrt(3) - 3) + sqrt(-I*sqrt(3) + 1)),
        #   z == sqrt(-1/2*I*sqrt(3) + 1/2)],
        #
        #  [y == -I, z == I],
        #
        #  [y == I, z == -I]]
        #

if __name__ == '__main__':
    TestGetSolutionSet().test__get_solution_set__1()
    # TestGetSolutionSet().test__get_solution_set__2()
    pass
