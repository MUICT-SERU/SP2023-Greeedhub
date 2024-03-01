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
        in_tab = [['a,1,2,3', 'b,u,v,w', 'c', 'd,q'], ['(aaaaa,ccccccc,3)', '[bbbbb,cccccccc]', 'c', 'd,q']]

        max_len = 5
        row_num = 10
        tab = refine_table( in_tab, max_len, row_num )

        for row in tab:
            print( row )
        print( tab )

        assert len( tab ) == 8
        assert [len( row ) for row in tab] == 8 * [4]
        assert str( tab ) == "[['a, ', 'b, ', 'c', 'd,q'], ['1, ', 'u, ', '', ''], ['2, ', 'v, ', '', ''], ['3, ', 'w, ', '', ''], ['', '', 'c', 'd,q'], ['(aaaaa, ', '[bbbbb, ', '', ''], ['ccccccc, ', 'cccccccc]', '', ''], ['3)', '', '', '']]"


if __name__ == '__main__':

    NSTools.filter( None )

    # TestConvertToTex().test__break_col()
    TestConvertToTex().test__refine_table()

    pass
