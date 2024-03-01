'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 6, 2017

@author: Niels Lubbes
'''

from linear_series.class_poly_ring import PolyRing

from linear_series.sage_interface import sage_QQ
from linear_series.sage_interface import sage__eval
from linear_series.sage_interface import sage_PolynomialRing
from linear_series.sage_interface import sage_factor
from linear_series.sage_interface import sage_NumberField
from linear_series.sage_interface import sage_FractionField


class TestClassPolyRing:

    def test__diff__1( self ):

        ring = PolyRing( 'x,y,v,w', True )
        ring.ext_num_field( 't^2 + 1' )
        x, y, v, w, a0 = ring.coerce( 'x,y,v,w,a0' )

        assert ring.diff( w - a0, w, 1 ) == 1


    def test__diff__2( self ):

        ring = PolyRing( 'x,y,v,w', True )
        ring.ext_num_field( 't^2 + 1' )
        x, y, v, w, a0 = ring.coerce( 'x,y,v,w,a0' )

        assert ring.diff( x ** 3 - a0, x, 3 ) == 6


    def test__diff__3( self ):

        ring = PolyRing( 'x,y,v,w', True )
        ring.ext_num_field( 't^2 + 1' )
        x, y, v, w, a0 = ring.coerce( 'x,y,v,w,a0' )

        d1 = ring.diff( y ** 2 * x ** 3 - a0, x, 2 )
        d2 = ring.diff( d1, y, 2 )

        assert d1 == 6 * y ** 2 * x
        assert d2 == 12 * x


    def test__quo( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + t + 1' )
        ring.ext_num_field( 't^3 + t + a0 + 3' )

        pol1 = ring.coerce( '(x+1)*(x^2+a0+1)' )
        pol2 = ring.coerce( '(x+1)' )
        assert str( pol1 ) == 'x^3 + x^2 + (a0 + 1)*x + a0 + 1'

        q = ring.quo( pol1, pol2 )
        assert str( q ) == 'x^2 + a0 + 1'


    def test__resultant( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + t + 1' )
        ring.ext_num_field( 't^3 + t + a0 + 3' )

        pol1 = ring.coerce( '(x+1)*(x^2+a0+1)' )
        pol2 = ring.coerce( 'x^5 + x + a0 + 3' )
        x = ring.coerce( 'x' )

        r = ring.resultant( pol1, pol2, x )
        assert str( r ) == '7*a0 + 2'


    def test__aux_gcd( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + t + 1' )
        ring.ext_num_field( 't^3 + t + a0 + 3' )

        agcd = ring.aux_gcd( '[x*y^2 + a1*y^3, y^5, x^5*y^5]' )
        assert str( agcd ) == '([(y, 2)], [x + a1*y, y^3, x^5*y^3])'


    def test__factor( self ):

        ring = PolyRing( 'x,y,z', True )

        ring.ext_num_field( 't^2 + t + 1' )
        ring.ext_num_field( 't^3 + t + a0 + 3' )

        pol = ring.coerce( '(x+1)*(x^2+a0+1)' )
        assert str( pol ) == 'x^3 + x^2 + (a0 + 1)*x + a0 + 1'
        assert str( sage_factor( pol ) ) == '(x + 1) * (x + a0) * (x - a0)'

        con = ring.coerce( 'a0' )
        assert str( sage_factor( con ) ) == 'a0'



    def test__ext_num_field( self ):

        ring = PolyRing( 'x,y,z', True )
        assert str( ring ) == 'QQ[x, y, z]'

        ring.ext_num_field( 't^2 + t + 1' )
        assert str( ring ) == 'QQ( <a0|t^2 + t + 1> )[x, y, z]'

        ring.ext_num_field( 't^3 + t + a0 + 3' )
        assert str( ring ) == 'QQ( <a0|t^2 + t + 1>, <a1|t^3 + t + a0 + 3>, <a2|t^2 + a1*t + a1^2 + 1> )[x, y, z]'

        a = ring.root_gens()
        x, y, z = ring.gens()

        pol = x ** 3 + x + a[0] + 3
        assert str( sage_factor( pol ) ) == '(x - a2) * (x - a1) * (x + a2 + a1)'

        mat = list( pol.sylvester_matrix( y ** 2 + x ** 2, x ) )
        assert str( mat ) == '[(1, 0, 1, a0 + 3, 0), (0, 1, 0, 1, a0 + 3), (1, 0, y^2, 0, 0), (0, 1, 0, y^2, 0), (0, 0, 1, 0, y^2)]'


    def test__sage_functionality_for_ext_num_field( self ):
        '''
        The class of "PolyRing" is built around Sage functionality
        as show cased in this method. Note in particular that 
        some functionality is not available in a "PolynomialRing" 
        over a "NumberField", but is available over a "FractionField".
        '''

        # construct a ring Rxyz over a number field
        R = sage_PolynomialRing( sage_QQ, 'a' )
        a = R.gens()[0]
        F0 = sage_NumberField( [a ** 2 + a + 1], 'a0' )
        a0 = F0.gens()[0]
        R.change_ring( F0 )
        F1 = sage_NumberField( [a ** 5 + a0 + a + 3], 'a1' )
        a1 = F1.gens()[0]
        R.change_ring( F1 )
        F2 = sage_NumberField( [a ** 2 + a + a0 ** 5 + a1 + 3], 'a2' )
        a2 = F2.gens()[0]
        R.change_ring( F2 )
        Rxyz = sage_PolynomialRing( F2, 'x,y,z', order = 'lex' )
        x, y, z = Rxyz.gens()

        # we consider some elements in Rxyz
        pol = x ** 2 + a0 * x + a1
        pol1 = x ** 5 + x + a0 + 3
        pol2 = x - a1

        # construct a ring PR over a fraction field
        ngens = F2.gens_dict().keys()  # a0, a1,...
        FF = sage_FractionField( sage_PolynomialRing( sage_QQ, ngens ) )
        pgens = Rxyz.gens_dict().keys()  # x, y, z
        PR = sage_PolynomialRing( FF, pgens )
        eval_dct = PR.gens_dict()
        eval_dct.update( FF.gens_dict() )

        # coerce elements to fraction field
        spol1 = sage__eval( str( pol1 ), eval_dct )
        spol2 = sage__eval( str( pol2 ), eval_dct )
        sx = sage__eval( str( x ), eval_dct )
        sy = sage__eval( str( y ), eval_dct )
        sz = sage__eval( str( z ), eval_dct )

        # in PR we can compute quo_rem, resultant and gcd
        squo = spol1.quo_rem( spol2 )[0]
        sres = spol1.resultant( spol2, sx )

        # coerce back to Rxyz
        eval_dct2 = Rxyz.gens_dict()
        eval_dct2.update( F2.gens_dict() )
        quo = sage__eval( str( squo ), eval_dct2 )
        res = sage__eval( str( sres ), eval_dct2 )

        # Values of variables:
        #
        # pol  = x^2 + a0*x + a1
        # pol1 = (x - a1) * (x^4 + a1*x^3 + a1^2*x^2 + a1^3*x + a1^4 + 1)
        # pol2 = x - a1
        # squo = x^4 + a1*x^3 + a1^2*x^2 + a1^3*x + a1^4 + 1
        # sres = -a1^5 - a1 - a0 - 3
        # res  = 0
        #
        if True:
            print( 'pol  =', sage_factor( pol ) )
            print( 'pol1 =', sage_factor( pol1 ) )
            print( 'pol2 =', sage_factor( pol2 ) )
            print( 'squo =', squo )
            print( 'sres =', sres )
            print( 'res =', res )


        #
        # pol1 and pol2 have a common factor
        # over the number field F2 so res=0 although sres!=0.
        #
        assert str( sage_factor( pol1 ) ) == '(x - a1) * (x^4 + a1*x^3 + a1^2*x^2 + a1^3*x + a1^4 + 1)'
        assert res == 0
        assert sres != 0



if __name__ == '__main__':
    TestClassPolyRing().test__diff__1()
    TestClassPolyRing().test__diff__2()
    TestClassPolyRing().test__diff__3()
    # TestClassPolyRing().test__quo()
    # TestClassPolyRing().test__resultant()
    # TestClassPolyRing().test__aux_gcd()
    # TestClassPolyRing().test__factor()
    # TestClassPolyRing().test__ext_num_field()
    # TestClassPolyRing().test_sage_functionality_for_ext_num_field()

    pass

