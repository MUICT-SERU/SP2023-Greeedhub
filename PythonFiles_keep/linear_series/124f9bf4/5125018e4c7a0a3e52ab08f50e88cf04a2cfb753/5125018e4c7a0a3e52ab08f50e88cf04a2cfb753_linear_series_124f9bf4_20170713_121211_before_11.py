'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 6, 2017
@author: Niels Lubbes
'''
from sage.all import *

from linear_series.class_poly_ring import *
from linear_series.class_linear_series import *
from linear_series.get_implicit import *



class TestGetImplicit:

    def test__get_implicit_image( self ):

        pmz_lst = [
         'x^2*v^2 - y^2*w^2',
         'x^2*v*w + y^2*v*w',
         'x^2*w^2 + y^2*w^2',
         'x*y*v^2 - y^2*v*w',
         'x*y*v*w - y^2*w^2',
         'y^2*v*w + x*y*w^2',
         'y^2*v^2 + y^2*w^2'
         ]
        ls = LinearSeries( pmz_lst, PolyRing( 'x,y,v,w', True ) )
        imp_lst = get_implicit_image( ls )

        # test whether "pmz_lst" substituted in "imp_lst" vanishes
        #
        ring = PolyRing( 'x0,x1,x2,x3,x4,x5,x6,x,y,v,w', True )
        x_lst = ring.coerce( 'x0,x1,x2,x3,x4,x5,x6' )
        p_lst = [ring.coerce( pmz ) for pmz in pmz_lst ]
        e_lst = ring.coerce( imp_lst )

        dct = { x_lst[i]:p_lst[i] for i in range( len( p_lst ) ) }
        r_lst = [ e.subs( dct ) for e in e_lst ]

        assert set( r_lst ) == {0}


if __name__ == '__main__':

    # TestGetImplicit().test__get_implicit_image()

    pass

