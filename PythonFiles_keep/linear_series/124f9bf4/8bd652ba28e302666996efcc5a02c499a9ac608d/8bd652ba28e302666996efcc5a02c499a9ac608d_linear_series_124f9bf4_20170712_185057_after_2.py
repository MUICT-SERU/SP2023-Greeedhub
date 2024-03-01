'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 10, 2017
@author: Niels Lubbes
'''

from sage.all import *

from linear_series.class_base_points import *
from class_test_tools import TestTools


class TestBasePoints( TestTools ):

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
        assert self.equal_output_strings( out, chk )


if __name__ == '__main__':
    # TestBasePoints().test__BasePointTree()
    pass
