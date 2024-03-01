'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 6, 2017
@author: Niels Lubbes
'''
from sage.all import *
from linear_series.class_poly_ring import *


class TestClassPolyRing:

    def test__quo__( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + t + 1' )
        ring.ext_num_field( 't^3 + t + a0 + 3' )

        # continue here.




    def test__aux_gcd__xy2_a1y3__y5__x5y5( self ):

        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + t + 1' )
        ring.ext_num_field( 't^3 + t + a0 + 3' )

        agcd = ring.aux_gcd( '[x*y^2 + a1*y^3, y^5, x^5*y^5]' )
        assert str( agcd ) == '([(y, 2)], [x + a1*y, y^3, x^5*y^3])'


    def test__ext_num_field__t2_t_1__t3_t_a0_3( self ):
        '''
        Test PolyRing object.
        '''
        ring = PolyRing( 'x,y,z', True )
        assert str( ring ) == 'QQ[x, y, z]'

        ring.ext_num_field( 't^2 + t + 1' )
        assert str( ring ) == 'QQ( <a0|t^2 + t + 1> )[x, y, z]'

        ring.ext_num_field( 't^3 + t + a0 + 3' )
        assert str( ring ) == 'QQ( <a0|t^2 + t + 1>, <a1|t^3 + t + a0 + 3>, <a2|t^2 + a1*t + a1^2 + 1> )[x, y, z]'

        a = ring.root_gens()
        x, y, z = ring.gens()

        pol = x ** 3 + x + a[0] + 3
        assert str( factor( pol ) ) == '(x - a2) * (x - a1) * (x + a2 + a1)'

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
            print( 'pol  =', factor( pol ) )
            print( 'pol1 =', factor( pol1 ) )
            print( 'pol2 =', factor( pol2 ) )
            print( 'squo =', squo )
            print( 'sres =', sres )
            print( 'res =', res )


        #
        # pol1 and pol2 have a common factor
        # over the number field F2 so res=0 although sres!=0.
        #
        assert str( factor( pol1 ) ) == '(x - a1) * (x^4 + a1*x^3 + a1^2*x^2 + a1^3*x + a1^4 + 1)'
        assert res == 0
        assert sres != 0



if __name__ == '__main__':
    # TestClassPolyRing().test_sage_functionality_for_ext_num_field()
    TestClassPolyRing().test__aux_gcd__xy2_a1y3__y5__x5y5()
    TestClassPolyRing().test__ext_num_field__t2_t_1__t3_t_a0_3()


    pass

