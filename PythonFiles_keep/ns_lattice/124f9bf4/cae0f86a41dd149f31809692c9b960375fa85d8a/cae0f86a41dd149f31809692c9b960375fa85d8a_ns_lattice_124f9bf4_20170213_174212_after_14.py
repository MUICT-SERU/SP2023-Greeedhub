'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 9, 2017
@author: Niels Lubbes
'''

from sage.all import *
from ns_lattice.ns_basis import *


class TestNSBasis:

    def test__get_base_changes__rank3( self ):

        nt = NSTools()
        nt.set_enable_tool_dct( False )
        mat_lst = get_base_changes( 3 )
        nt.set_enable_tool_dct( True )

        chk_lst = []
        chk_lst += [ [( 1, -1, 0 ), ( 1, 0, -1 ), ( 1, -1, -1 )] ]
        chk_lst += [ [( 1, 0, 0 ), ( 0, 0, 1 ), ( 0, 1, 0 )] ]
        chk_lst += [ [( 1, 0, 0 ), ( 0, 1, 0 ), ( 0, 0, 1 )] ]

        assert mat_lst == [ matrix( chk ) for chk in chk_lst ]


    def test__get_base_changes__rank3_12( self ):

        nt = NSTools()
        nt.set_enable_tool_dct( False )
        mat_lst = get_base_changes( 3, [Div( [0, 1, -1] )] )
        nt.set_enable_tool_dct( True )

        chk_lst = []
        chk_lst += [ [( 1, 0, 0 ), ( 0, 1, 0 ), ( 0, 0, 1 )] ]

        assert mat_lst == [ matrix( chk ) for chk in chk_lst ]


    def test__get_base_changes__rank4( self ):

        nt = NSTools()
        nt.set_enable_tool_dct( False )
        mat_lst = get_base_changes( 4 )
        nt.set_enable_tool_dct( True )

        chk_lst = []
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, 0, -1, -1 ), ( 1, -1, 0, -1 ), ( 1, -1, -1, 0 )] ]
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, -1, 0, -1 ), ( 1, 0, -1, -1 ), ( 1, -1, -1, 0 )] ]
        chk_lst += [ [( 1, -1, 0, 0 ), ( 1, 0, -1, 0 ), ( 0, 0, 0, 1 ), ( 1, -1, -1, 0 )] ]
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, 0, -1, -1 ), ( 1, -1, -1, 0 ), ( 1, -1, 0, -1 )] ]
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, -1, -1, 0 ), ( 1, 0, -1, -1 ), ( 1, -1, 0, -1 )] ]
        chk_lst += [ [( 1, -1, 0, 0 ), ( 1, 0, 0, -1 ), ( 0, 0, 1, 0 ), ( 1, -1, 0, -1 )] ]
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, -1, 0, -1 ), ( 1, -1, -1, 0 ), ( 1, 0, -1, -1 )] ]
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, -1, -1, 0 ), ( 1, -1, 0, -1 ), ( 1, 0, -1, -1 )] ]
        chk_lst += [ [( 1, 0, -1, 0 ), ( 1, 0, 0, -1 ), ( 0, 1, 0, 0 ), ( 1, 0, -1, -1 )] ]
        chk_lst += [ [( 1, 0, -1, 0 ), ( 1, 0, 0, -1 ), ( 1, 0, -1, -1 ), ( 0, 1, 0, 0 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 0, 0, 1 ), ( 0, 0, 1, 0 ), ( 0, 1, 0, 0 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 0, 1, 0 ), ( 0, 0, 0, 1 ), ( 0, 1, 0, 0 )] ]
        chk_lst += [ [( 1, -1, 0, 0 ), ( 1, 0, 0, -1 ), ( 1, -1, 0, -1 ), ( 0, 0, 1, 0 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 0, 0, 1 ), ( 0, 1, 0, 0 ), ( 0, 0, 1, 0 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 1, 0, 0 ), ( 0, 0, 0, 1 ), ( 0, 0, 1, 0 )] ]
        chk_lst += [ [( 1, -1, 0, 0 ), ( 1, 0, -1, 0 ), ( 1, -1, -1, 0 ), ( 0, 0, 0, 1 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 0, 1, 0 ), ( 0, 1, 0, 0 ), ( 0, 0, 0, 1 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 1, 0, 0 ), ( 0, 0, 1, 0 ), ( 0, 0, 0, 1 )] ]

        assert mat_lst == [ matrix( chk ) for chk in chk_lst ]


    def test__get_base_changes__rank4_12( self ):

        nt = NSTools()
        nt.set_enable_tool_dct( False )
        mat_lst = get_base_changes( 4, [Div( [0, 1, -1, 0] )] )
        nt.set_enable_tool_dct( True )

        chk_lst = []
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, 0, -1, -1 ), ( 1, -1, 0, -1 ), ( 1, -1, -1, 0 )] ]
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, 0, -1, -1 ), ( 1, -1, -1, 0 ), ( 1, -1, 0, -1 )] ]
        chk_lst += [ [( 1, -1, 0, 0 ), ( 1, 0, 0, -1 ), ( 0, 0, 1, 0 ), ( 1, -1, 0, -1 )] ]
        chk_lst += [ [( 2, -1, -1, -1 ), ( 1, -1, -1, 0 ), ( 1, 0, -1, -1 ), ( 1, -1, 0, -1 )] ]
        chk_lst += [ [( 1, -1, 0, 0 ), ( 1, 0, 0, -1 ), ( 1, -1, 0, -1 ), ( 0, 0, 1, 0 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 1, 0, 0 ), ( 0, 0, 0, 1 ), ( 0, 0, 1, 0 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 0, 0, 1 ), ( 0, 1, 0, 0 ), ( 0, 0, 1, 0 )] ]
        chk_lst += [ [( 1, 0, 0, 0 ), ( 0, 1, 0, 0 ), ( 0, 0, 1, 0 ), ( 0, 0, 0, 1 )] ]

        assert mat_lst == [ matrix( chk ) for chk in chk_lst ]


