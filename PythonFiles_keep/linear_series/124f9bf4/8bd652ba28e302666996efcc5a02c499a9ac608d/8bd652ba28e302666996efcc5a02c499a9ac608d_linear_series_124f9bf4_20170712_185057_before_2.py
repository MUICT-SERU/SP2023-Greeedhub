'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 10, 2017
@author: Niels Lubbes
'''

from sage.all import *

from linear_series.class_base_points import *

class TestBasePoints:

    def __clean__( self, s, ch_lst ):
        for ch in ch_lst:
            while ch in s:
                s = s.replace( ch, '' )
        return s

    def test__BasePointTree( self ):

        bp_tree = BasePointTree()
        bp = bp_tree.add( 'z', ( 0, 0 ), 1 )
        bp = bp.add( 't', ( 0, 0 ), 1 )
        bp = bp.add( 't', ( -1, 0 ), 1 )
        bp = bp.add( 't', ( 0, 0 ), 1 )

        out = str( bp_tree )
        chk = """
                chart=z, depth=0, mult=1, sol=(0, 0), None
                    chart=t, depth=1, mult=1, sol=(0, 0), None
                        chart=t, depth=2, mult=1, sol=(-1, 0), None
                            chart=t, depth=3, mult=1, sol=(0, 0), None        
              """
        out = self.__clean__( out, [' ', '\n', '\t'] )
        chk = self.__clean__( chk, [' ', '\n', '\t'] )
        assert out == chk


if __name__ == '__main__':

    TestBasePoints().test__BasePointTree()

    pass
