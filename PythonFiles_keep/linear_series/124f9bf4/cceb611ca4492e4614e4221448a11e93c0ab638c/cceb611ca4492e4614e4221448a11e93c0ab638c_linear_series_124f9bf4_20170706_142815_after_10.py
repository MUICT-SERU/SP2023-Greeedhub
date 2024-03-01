'''
Created on Aug 6, 2016
@author: Niels Lubbes

Here functionality of "linear_series" package is tested.
Our methods use Sage.  
The method names in this module are of the form: 
    "test_[method name to be tested]_[index]()"
For output we use "dprint()" in "verbose.py".
'''

from sage.all import *

from verbose import *
from class_poly_ring import *
from class_linear_series import *
from class_base_points import *
from get_implicit import *


def test_poly_ring_0():
    '''
    The class of "PolyRing" is built around Sage functionality
    as show cased in this method. Note in particular that 
    some functionality is not available in a "PolynomialRing" 
    over a "NumberField", but is available over a "FractionField".
    '''

    # construct a ring Rxyz over a number field
    R = PolynomialRing( QQ, 'a' )
    a = R.gens()[0]
    F0 = NumberField( [a ** 2 + a + 1], 'a0' )
    a0 = F0.gens()[0]
    R.change_ring( F0 )
    F1 = NumberField( [a ** 5 + a0 + a + 3], 'a1' )
    a1 = F1.gens()[0]
    R.change_ring( F1 )
    F2 = NumberField( [a ** 2 + a + a0 ** 5 + a1 + 3], 'a2' )
    a2 = F2.gens()[0]
    R.change_ring( F2 )
    Rxyz = PolynomialRing( F2, var( 'x,y,z' ), order = 'lex' )
    x, y, z = Rxyz.gens()

    # we consider some elements in Rxyz
    pol = x ** 2 + a0 * x + a1
    pol1 = x ** 5 + x + a0 + 3
    pol2 = x - a1

    # construct a ring PR over a fraction field
    ngens = F2.gens_dict().keys()  # a0, a1,...
    FF = FractionField( PolynomialRing( QQ, ngens ) )
    pgens = Rxyz.gens_dict().keys()  # x, y, z
    PR = PolynomialRing( FF, pgens )
    eval_dct = PR.gens_dict()
    eval_dct.update( FF.gens_dict() )

    # coerce elements to fraction field
    spol1 = sage_eval( str( pol1 ), eval_dct )
    spol2 = sage_eval( str( pol2 ), eval_dct )
    sx = sage_eval( str( x ), eval_dct )
    sy = sage_eval( str( y ), eval_dct )
    sz = sage_eval( str( z ), eval_dct )

    # in PR we can compute quo_rem, resultant and gcd
    squo = spol1.quo_rem( spol2 )[0]
    sres = spol1.resultant( spol2, sx )

    # coerce back to Rxyz
    eval_dct2 = Rxyz.gens_dict()
    eval_dct2.update( F2.gens_dict() )
    quo = sage_eval( str( squo ), eval_dct2 )
    res = sage_eval( str( sres ), eval_dct2 )

    # note that pol1 and pol2 have a common factor
    # over the number field F2 so res=0 although sres!=0.
    #
    dprint( 'pol, pol1, pol2 =', ( pol, pol1, pol2 ) )
    dprint( 'pol1 =', factor( pol1 ) )
    dprint( factor( x ** 5 + x + a0 + 3 ) )
    dprint( 'squo =', squo )
    dprint( 'sres =', sres )
    dprint( 'res =', res )

def test_poly_ring_1():
    '''
    Test PolyRing object.
    '''

    ring = PolyRing( 'x,y,z' )
    ring.ext_num_field( 't^2 + t + 1' )

    dprint( ring )

    ring.ext_num_field( 't^3 + t + a0 + 3' )

    dprint( ring )

    a = ring.root_gens()
    x, y, z = ring.gens()
    pol = x ** 2 + a[0] * x + a[1]

    dprint( factor( pol ) )
    dprint( factor( x ** 3 + x + a[0] + 3 ) )

    dprint( ring.aux_gcd( '[x*y^2 + a1*y^3, y^5, x^5*y^5]' ) )

    mat = pol.sylvester_matrix( y ** 2 + x ** 2, x )
    dprint( mat )

    dprint()


def test_linear_series_0():
    '''
    Test LinearSeries object.
    '''

    ring = PolyRing( 'x,y,z' )
    x, y, z = ring.gens()
    pol_lst = [x ** 2 * z + y ** 2 * z, y ** 3 + z ** 3]

    ls = LinearSeries( pol_lst, ring )

    xls = ls.copy().chart( x )

    dprint( xls )

    sol_lst = xls.get_solution_set()

    dprint( len( sol_lst ), sol_lst )

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
    dprint( False, 'ls_main.py' )

    idx = 0
    for pol_lst in pol_lst_lst:

        PolyRing.num_field = QQ
        ls = LinearSeries( pol_lst )

        dprint( idx )
        dprint( ls )
        bp_tree = ls.get_bp_tree()
        dprint( bp_tree )

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
    dprint( ring )

    ring.ext_num_field( 't^3 + a0' )
    dprint( ring )

    a0, a1 = ring.root_gens()
    x, y, z = ring.gens()

    pol_lst = [x ** 2 + a0 * y * z, y + a1 * z + x ]

    ls = LinearSeries( pol_lst, ring )
    dprint( ls )

    bp_tree = ls.get_bp_tree()
    dprint( bp_tree )


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
    dprint( ls )

    bp_tree = ls.get_bp_tree()
    dprint( bp_tree )


def test_get_linear_series_0():
    '''
    Test "get_linear_series.get_mon_lst()".
    '''

    mon_lst = get_mon_lst( 2, PolyRing( 'x,y,z' ).gens() )
    dprint( len( mon_lst ), mon_lst )

    mon_lst = get_mon_lst( 1, PolyRing( 'x,y,v,w' ).gens() )
    dprint( len( mon_lst ), mon_lst )

    mon_lst = get_mon_lst( 2, PolyRing( 'x,y,v,w' ).gens() )
    dprint( len( mon_lst ), mon_lst )


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
    dprint( bp_tree )

    ls = LinearSeries.get( 2, bp_tree )
    dprint( ls )

    dprint( 20 * '==' )
    dprint( ls.get_bp_tree() )


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
    dprint( bp_tree )

    # construct corresponding linear series of bi-degree (2,2)
    # and 2 simple complex conjugate base points
    ls = LinearSeries.get( 2, bp_tree )
    dprint( ls.get_bp_tree() )

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
    dprint( bp_tree )

    dprint( 'pol_lst =' )
    for pol in ls.pol_lst:
        dprint( '\t', factor( pol ) )


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
    dprint( bp_tree )

    # construct corresponding linear series of bi-degree (1,1)
    # and 2 simple complex conjugate base points
    ls = LinearSeries.get( 1, bp_tree )
    dprint( ls.get_bp_tree() )

    # linear series of bidegree (1,1) with same base points
    pol_lst = ['x * v - y * w', 'y * v + x * w' ]
    ls = LinearSeries( pol_lst, PolyRing( 'x,y,v,w' ) )
    bp_tree = ls.get_bp_tree()
    dprint( bp_tree )


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
        dprint( 'idx =', idx )
        dprint( 'pol =', pol )
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
    dprint( bp_tree )

    # implicit image in projective 6-space
    # of map associated to linear series
    imp_lst = get_implicit_image( ls )

    # compute Hilbert polynomial in QQ[x0,...,x6]
    ring = PolynomialRing( QQ, [ 'x' + str( i ) for i in range( 7 )] )
    x_lst = ring.gens()
    imp_lst = sage_eval( str( imp_lst ), ring.gens_dict() )
    hpol = ring.ideal( imp_lst ).hilbert_polynomial()
    hdeg = hpol.diff().diff()
    dprint( hdeg, hpol )

    # equation of unit sphere is not in the ideal
    s_pol = sum( [-x_lst[0] ** 2] + [x ** 2 for x in x_lst[1:]] )
    dprint( 'Inside sphere?: ', s_pol in ideal( imp_lst ) )

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
        dprint( 'sig =', sig, c_lst )

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
    dprint( 'pmz_lst =', pmz_lst )
    dprint( 'imp_lst =', imp_lst )
    dprint( 'M_pol   =', M_pol )
    dprint( 'tests   =', vx * M * vx == M_pol, M_pol in ideal( imp_lst ), M * V == V * D )
    dprint( 'M       =', list( M ) )
    dprint( 'D diag. =', D.diagonal() )
    dprint( 'J diag. =', J.diagonal() )
    dprint( 'U       =', list( U ) )
    dprint( 'U.T*J*U =', list( U.T * J * U ) )




if __name__ == '__main__':


    #  Debug output settings
    #
    dprint( False, 'ls_main.py' )  # show only output from 'ls_main.py'
    # dprint( True )  # show all output
    tprint( True )  # show timing

    #########################################
    #                                       #
    # Uncomment one or more test methods    #
    #                                       #
    #########################################

    # test_poly_ring_0() #        test Sage rings and number field functionality
    # test_poly_ring_1() #        test PolyRing object
    # test_linear_series_0() #    test LinearSeries object
    test_get_base_points_0()  # obtain base points of several examples of linear series
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

    # end timing
    tprint()

    print
    print 'The End'
