'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 6, 2017
@author: Niels Lubbes
'''
from sage.all import *

from linear_series.class_ls_tools import LSTools
from linear_series.class_poly_ring import *
from linear_series.class_linear_series import *


class TestGetBasePointTree:

    def __clean__( self, s, ch_lst ):
        for ch in ch_lst:
            while ch in s:
                s = s.replace( ch, '' )
        return s


    def test__get_base_point_tree( self ):
        ring = PolyRing( 'x,y,z', True )
        ring.ext_num_field( 't^2 + 1' )
        ring.ext_num_field( 't^3 + a0' )

        ls = LinearSeries( ['x^2+a0*y*z', 'y+a1*z+x' ], ring )

        out = str( ls.get_bp_tree() )
        chk = """
            { 2, <<x^2 + a0*y*z, x + y + a1*z>>, QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1>, <a2|t^2 - a0*t - a0*a1> )[x, y, z] }
            chart=z, depth=0, mult=1, sol=(-a2 + a0, a2 - a1 - a0), { 2, <<x^2 + a0*y, x + y + a1>>, QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1>, <a2|t^2 - a0*t - a0*a1> )[x, y] }
            chart=z, depth=0, mult=1, sol=(a2, -a2 - a1), { 2, <<x^2 + a0*y, x + y + a1>>, QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1>, <a2|t^2 - a0*t - a0*a1> )[x, y] }
            """
        out = self.__clean__( out, [' ', '\n', '\t'] )
        chk = self.__clean__( chk, [' ', '\n', '\t'] )
        assert out == chk

        assert out == chk


if __name__ == '__main__':

    # LSTools.filter( 'test_get_linear_series.py' )
    # TestGetBasePointTree().test__get_base_point_tree()

    pass
