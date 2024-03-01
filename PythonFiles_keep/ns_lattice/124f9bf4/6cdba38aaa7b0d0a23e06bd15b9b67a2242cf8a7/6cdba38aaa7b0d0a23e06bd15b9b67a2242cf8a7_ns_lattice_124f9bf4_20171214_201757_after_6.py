'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes


'''

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.convert_to_tex import break_col
from ns_lattice.convert_to_tex import refine_table



class TestConvertToTex:


    def test__break_col( self ):
        col = 'a,1,2,3'
        max_len = 4
        row_num = 5
        lst = break_col( col, max_len, row_num )
        print( lst )

        assert len( lst ) == row_num
        assert lst == ['a, 1, ', '2, 3, ', '', '', '']


    def test__refine_table( self ):
        in_tab = [['a,1,2,3', 'b,u,v,w', 'c', 'd,q']]

        max_len = 5
        row_num = 10
        tab = refine_table( in_tab, max_len, row_num )

        for row in tab:
            print( row )

        assert len( tab ) == 2
        assert len( tab[0] ) == len( tab[1] ) == 4


if __name__ == '__main__':

    NSTools.filter( None )

    # TestConvertToTex().test__break_col()
    TestConvertToTex().test__refine_table()

    pass
