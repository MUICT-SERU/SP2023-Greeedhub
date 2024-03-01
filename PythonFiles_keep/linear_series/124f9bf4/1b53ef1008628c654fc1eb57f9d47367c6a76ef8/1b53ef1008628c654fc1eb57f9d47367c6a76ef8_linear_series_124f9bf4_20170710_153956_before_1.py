'''
Created on Aug 6, 2016
@author: Niels Lubbes

Here functionality of "linear_series" package is tested.
Our methods use Sage.  
The method names in this module are of the form: 
    "test_[method name to be tested]_[index]()"
For output we use "lt.p()" in "verbose.py".
'''

from sage.all import *

from class_ls_tools import LSTools
from class_poly_ring import *
from class_linear_series import *
from class_base_points import *
from get_implicit import *


lt = LSTools()






def test_linear_series_0():
    '''
    Test LinearSeries object.
    '''

    ring = PolyRing( 'x,y,z' )
    x, y, z = ring.gens()
    pol_lst = [x ** 2 * z + y ** 2 * z, y ** 3 + z ** 3]

    ls = LinearSeries( pol_lst, ring )

    xls = ls.copy().chart( x )

    lt.p( xls )

    sol_lst = xls.get_solution_set()

    lt.p( len( sol_lst ), sol_lst )

    # y,z=var('y,z')
    # pol_lst = [y^2*z + z, y^3 + z^3]
    # solve( pol_lst )
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

def test_get_base_points_0():
    '''
    We obtain (infinitely near) base points of several 
    examples of linear series in order to test
    "get_base_point_tree.get_bp_tree()".
    '''
    pol_lst_lst = []

    # 0
    pol_lst_lst += [['x^2*z + y^2*z', 'y^3 + z^3']]

    # 1
    pol_lst_lst += [['x^3*z^2 + y^5', 'x^5']]

    # 2 (example from PhD thesis)
    pol_lst_lst += [['x^2', 'x*z + y^2']]

    # 3
    pol_lst_lst += [['x^2 + y^2', 'x*z + y^2']]

    # 4
    pol_lst_lst += [['x*z', 'y^2', 'y*z', 'z^2']]

    # 5
    pol_lst_lst += [['x^5', 'y^2*z^3']]

    # 6
    pol_lst_lst += [['x^2*y', 'x*y^2', 'x*y*z', '( x^2 + y^2 + z^2 )*z' ]]

    # 7 (weighted projective plane P(2:1:1))
    pol_lst_lst += [['z^6'    , 'y*z^5'    , 'y^2*z^4'    ,
                     'y^3*z^3', 'y^4*z^2'  , 'y^5*z'      , 'y^6',
                     'x^2*z^4', 'x^2*y*z^3', 'x^2*y^2*z^2', 'x^3*z^3']]

    # 8 (provided by Martin Weimann)
    pol_lst_lst += [['y^2*(x^3+x^2*z+2*x*z^2+z^3)+y*(2*x^3+2*x*z^2)*z+z^2*(x^3-x^2*z+x*z^2)',
                    'z^5' ]]

    # 9
    pol_lst_lst += [['x^3*y^4+x*y^4*z^2+3*x^2*y^3*z^2+3*x*y^2*z^4+y',
                    'z^7']]

    # 10 (degree 6 del Pezzo in S^5, which is the orbital product of 2 circles)
    pol_lst_lst += [[
        'x^2*y^2 + 6/5*x^2*y*z + 17/5*x^2*z^2 + y^2*z^2 + 6/5*y*z^3 + 17/5*z^4',
        '8/5*x^2*y*z + 6/5*x^2*z^2 + 8/5*y*z^3 + 6/5*z^4',
        'x^2*y^2 + 6/5*x^2*y*z + 7/5*x^2*z^2 + y^2*z^2 + 6/5*y*z^3 + 7/5*z^4',
        '4*x*z^3',
        '2*x^2*z^2 - 2*z^4',
        '-6/5*x^2*y*z - 2/5*x^2*z^2 - 4*x*z^3 + 6/5*y*z^3 + 2/5*z^4',
        '-2*x^2*z^2 + 12/5*x*y*z^2 + 4/5*x*z^3 + 2*z^4'
       ]]


    BasePointTree.short = True

    #
    # Uncomment following line for disabling output of debug info:
    #
    lt.p( False, 'ls_main.py' )

    idx = 0
    for pol_lst in pol_lst_lst:

        PolyRing.num_field = QQ
        ls = LinearSeries( pol_lst )

        lt.p( idx )
        lt.p( ls )
        bp_tree = ls.get_bp_tree()
        lt.p( bp_tree )

        idx += 1


def test_get_base_points_1():
    '''
    We obtain (infinitely near) base points of several 
    examples of linear series defined over a number field 
    in order to test
    "get_base_point_tree.get_bp_tree()".
    '''
    ring = PolyRing( 'x,y,z' )

    ring.ext_num_field( 't^2 + 1' )
    lt.p( ring )

    ring.ext_num_field( 't^3 + a0' )
    lt.p( ring )

    a0, a1 = ring.root_gens()
    x, y, z = ring.gens()

    pol_lst = [x ** 2 + a0 * y * z, y + a1 * z + x ]

    ls = LinearSeries( pol_lst, ring )
    lt.p( ls )

    bp_tree = ls.get_bp_tree()
    lt.p( bp_tree )


def test_get_base_points_2():
    '''
    Test "get_base_point_tree.get_bp_tree()".
    We consider linear series defined by bi-homogeneous polynomials,
    which are defined on P^1xP^1 
    (the fiber product of the projective line with itself). 
    The coordinate functions of P^1xP^1 are (x:y)(v:w).
    '''

    pol_lst = [ '17/5*v^2*x^2 + 6/5*v*w*x^2 + w^2*x^2 + 17/5*v^2*y^2 + 6/5*v*w*y^2 + w^2*y^2',
                '6/5*v^2*x^2 + 8/5*v*w*x^2 + 6/5*v^2*y^2 + 8/5*v*w*y^2',
                '7/5*v^2*x^2 + 6/5*v*w*x^2 + w^2*x^2 + 7/5*v^2*y^2 + 6/5*v*w*y^2 + w^2*y^2',
                '4*v^2*x*y',
                '-2*v^2*x^2 + 2*v^2*y^2',
                '2/5*v^2*x^2 + 6/5*v*w*x^2 - 4*v^2*x*y - 2/5*v^2*y^2 - 6/5*v*w*y^2',
                '2*v^2*x^2 + 4/5*v^2*x*y + 12/5*v*w*x*y - 2*v^2*y^2' ]

    ls = LinearSeries( pol_lst, PolyRing( 'x,y,v,w' ) )
    lt.p( ls )

    bp_tree = ls.get_bp_tree()
    lt.p( bp_tree )


def test_get_linear_series_0():
    '''
    Test "get_linear_series.get_mon_lst()".
    '''

    mon_lst = get_mon_lst( 2, PolyRing( 'x,y,z' ).gens() )
    lt.p( len( mon_lst ), mon_lst )

    mon_lst = get_mon_lst( 1, PolyRing( 'x,y,v,w' ).gens() )
    lt.p( len( mon_lst ), mon_lst )

    mon_lst = get_mon_lst( 2, PolyRing( 'x,y,v,w' ).gens() )
    lt.p( len( mon_lst ), mon_lst )


def test_get_linear_series_1():
    '''
    Test "get_linear_series.get_linear_series()".
    '''

    # Example from PhD thesis (page 159).
    bp_tree = BasePointTree()
    bp = bp_tree.add( 'z', ( 0, 0 ), 1 )
    bp = bp.add( 't', ( 0, 0 ), 1 )
    bp = bp.add( 't', ( -1, 0 ), 1 )
    bp = bp.add( 't', ( 0, 0 ), 1 )
    lt.p( bp_tree )

    ls = LinearSeries.get( 2, bp_tree )
    lt.p( ls )

    lt.p( 20 * '==' )
    lt.p( ls.get_bp_tree() )


def test_get_linear_series_2():
    '''
    Test "get_linear_series.get_linear_series()"
    
    We construct bi-homogeneous linear series in (x:y)(v:w)
    of bi-degree (2,2). 
    '''

    # construct ring over Gaussian rationals
    ring = PolyRing( 'x,y,v,w' )
    ring.ext_num_field( 't^2 + 1' )
    a0 = ring.root_gens()[0]

    # setup base point tree for 2 simple
    # complex conjugate base points.
    bp_tree = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bp = bp_tree.add( 'xv', ( -a0, a0 ), 1 )
    bp = bp_tree.add( 'xv', ( a0, -a0 ), 1 )
    lt.p( bp_tree )

    # construct corresponding linear series of bi-degree (2,2)
    # and 2 simple complex conjugate base points
    ls = LinearSeries.get( 2, bp_tree )
    lt.p( ls.get_bp_tree() )

    # linear series of bidegree (2,2) with same base points
    pol_lst = [
         'x^2*v^2 - y^2*w^2',
         'x^2*v*w + y^2*v*w',
         'x^2*w^2 + y^2*w^2',
         'x*y*v^2 - y^2*v*w',
         'x*y*v*w - y^2*w^2',
         'y^2*v*w + x*y*w^2',
         'y^2*v^2 + y^2*w^2'
         ]
    ls = LinearSeries( pol_lst, PolyRing( 'x,y,v,w' ) )
    bp_tree = ls.get_bp_tree()
    lt.p( bp_tree )

    lt.p( 'pol_lst =' )
    for pol in ls.pol_lst:
        lt.p( '\t', factor( pol ) )


def test_get_linear_series_3():
    '''
    Test "get_linear_series.get_linear_series()"
    
    We construct bi-homogeneous linear series in (x:y)(v:w)
    of bi-degree (1,1). 
    '''

    # construct ring over Gaussian rationals
    ring = PolyRing( 'x,y,v,w' )
    ring.ext_num_field( 't^2 + 1' )
    a0 = ring.root_gens()[0]

    # setup base point tree for 2 simple
    # complex conjugate base points.
    bp_tree = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bp = bp_tree.add( 'xv', ( -a0, a0 ), 1 )
    bp = bp_tree.add( 'xv', ( a0, -a0 ), 1 )
    lt.p( bp_tree )

    # construct corresponding linear series of bi-degree (1,1)
    # and 2 simple complex conjugate base points
    ls = LinearSeries.get( 1, bp_tree )
    lt.p( ls.get_bp_tree() )

    # linear series of bidegree (1,1) with same base points
    pol_lst = ['x * v - y * w', 'y * v + x * w' ]
    ls = LinearSeries( pol_lst, PolyRing( 'x,y,v,w' ) )
    bp_tree = ls.get_bp_tree()
    lt.p( bp_tree )


def test_get_implicit_0():
    '''
    Test "get_implicit.get_implicit_projection()".
    '''

    input_lst = []

    # 0
    input_lst += [( 3, [ 'x^2*z+y^2*z+z^2*z', 'x^2*y', 'x*y^2', 'x*y*z' ] )]

    # 1
    input_lst += [( 7, [ 'x^2*y+y^3+y^2*x+x^3', 'x*z^2', 'y*z^2', 'z^3' ] )]

    # 2
    input_lst += [( 8, [ 'x^2*y^2', 'x^2*z^2 + x*y^3', 'y^2*z^2', 'y^4' ] )]

    idx = 0
    for deg, pol_lst in input_lst:
        ls = LinearSeries( pol_lst )
        pol = ls.get_implicit_projection( deg )
        lt.p( 'idx =', idx )
        lt.p( 'pol =', pol )
        idx += 1


def test_get_implicit_1():
    '''
    Test "get_implicit.get_implicit_image()".
    
    '''

    # parametrization of degree 6 del Pezzo surface
    # in projective 6-space
    pmz_lst = [
         'x^2*v^2 - y^2*w^2',
         'x^2*v*w + y^2*v*w',
         'x^2*w^2 + y^2*w^2',
         'x*y*v^2 - y^2*v*w',
         'x*y*v*w - y^2*w^2',
         'y^2*v*w + x*y*w^2',
         'y^2*v^2 + y^2*w^2'
         ]
    ls = LinearSeries( pmz_lst, PolyRing( 'x,y,v,w' ) )

    # base points of linear series
    bp_tree = ls.get_bp_tree()
    lt.p( bp_tree )

    # implicit image in projective 6-space
    # of map associated to linear series
    imp_lst = get_implicit_image( ls )

    # compute Hilbert polynomial in QQ[x0,...,x6]
    ring = PolynomialRing( QQ, [ 'x' + str( i ) for i in range( 7 )] )
    x_lst = ring.gens()
    imp_lst = sage_eval( str( imp_lst ), ring.gens_dict() )
    hpol = ring.ideal( imp_lst ).hilbert_polynomial()
    hdeg = hpol.diff().diff()
    lt.p( hdeg, hpol )

    # equation of unit sphere is not in the ideal
    s_pol = sum( [-x_lst[0] ** 2] + [x ** 2 for x in x_lst[1:]] )
    lt.p( 'Inside sphere?: ', s_pol in ideal( imp_lst ) )

    # compute random quadrics containing del Pezzo surface
    # until a quadric with signature (1,6) is found
    # or set a precomputed quadric with given "c_lst"
    sig = []
    while sorted( sig ) != [0, 1, 6]:

        # set coefficient list
        # c_lst = [1, 1, -1, 1, -1, 1, 1, -1, 1, 1, -1]
        c_lst = [-1, -1, 0, 0, 0, -1, 1, 0, -1, -1, -1]
        # c_lst = []
        if c_lst == []:
            lst = [-1, 0, 1]
            for imp in imp_lst:
                idx = int( ZZ.random_element( 0, len( lst ) ) )
                c_lst += [ lst[idx] ]

        # obtain quadric in ideal from "c_lst"
        i_lst = range( len( imp_lst ) )
        M_pol = [ c_lst[i] * imp_lst[i] for i in i_lst if imp_lst[i].total_degree() == 2 ]
        M_pol = sum( M_pol )

        # eigendecomposition
        M = invariant_theory.quadratic_form( M_pol, x_lst ).as_QuadraticForm().matrix()
        M = matrix( QQ, M )
        vx = vector( x_lst )
        D, V = M.eigenmatrix_right()

        # determine signature of quadric
        num_pos = len( [ d for d in D.diagonal() if d > 0 ] )
        num_neg = len( [ d for d in D.diagonal() if d < 0 ] )
        num_zer = len( [ d for d in D.diagonal() if d == 0 ] )
        sig = [ num_pos, num_neg, num_zer ]
        lt.p( 'sig =', sig, c_lst )

    # output of M.eigenmatrix_right() ensures that
    # D has signature either (--- --- +) or (- +++ +++)
    #
    if num_pos < num_neg:  # (--- --- +) ---> (+ --- ---)
        V.swap_columns( 0, 6 )
        D.swap_columns( 0, 6 )
        D.swap_rows( 0, 6 )

    # diagonal orthonormalization
    # note: M == W.T*D*W == W.T*L.T*J*L*W = U.T*J*U
    W = matrix( [col / col.norm() for col in V.columns()] )
    J = []
    for d in D.diagonal():
        if d > 0:
            J += [1]
        elif d < 0:
            J += [-1]
    J = diagonal_matrix( J )
    L = diagonal_matrix( [ d.abs().sqrt() for d in D.diagonal()] )
    U = L * W

    # output
    lt.p( 'pmz_lst =', pmz_lst )
    lt.p( 'imp_lst =', imp_lst )
    lt.p( 'M_pol   =', M_pol )
    lt.p( 'tests   =', vx * M * vx == M_pol, M_pol in ideal( imp_lst ), M * V == V * D )
    lt.p( 'M       =', list( M ) )
    lt.p( 'D diag. =', D.diagonal() )
    lt.p( 'J diag. =', J.diagonal() )
    lt.p( 'U       =', list( U ) )
    lt.p( 'U.T*J*U =', list( U.T * J * U ) )


if __name__ == '__main__':

    lt.start_timer()
    lt.filter( '__main__.py' )  # output only from this module

    ###############################################
    # (un)comment usecases for this package below #
    ###############################################

    test_poly_ring_0()  #        test Sage rings and number field functionality
    # test_poly_ring_1() #        test PolyRing object
    # test_linear_series_0() #    test LinearSeries object
    # test_get_base_points_0()  # obtain base points of several examples of linear series
    # test_get_base_points_1() # obtain base points with linear series over QQ(a0,a1)
    # test_get_base_points_2()  # obtain base points with linear series on P^1xP^1
    # test_get_linear_series_0()  # test "get_mon_lst()"
    # test_get_linear_series_1()  # example from PhD thesis (page 159)
    # test_get_linear_series_2()  # example of degree 6 del Pezzo.
    # test_get_linear_series_3()  # example of family degree 6 del Pezzo.
    # test_get_implicit_0() # obtain implicit projected surface from linear series
    # test_get_implicit_1()

    #########################################
    #                                       #
    # End of list of test methods.          #
    #                                       #
    #########################################

    lt.stop_timer()
    print
    print( 'The End' )

