'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes


'''

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.convert_to_tex import break_col
from ns_lattice.convert_to_tex import refine_table
from ns_lattice.convert_to_tex import cls_to_tex

from ns_lattice.class_dp_lattice import DPLattice
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.class_div import Div


class TestConvertToTex:


    def test__break_col( self ):
        col = '1234567,12,345,12,34567'
        max_len = 10
        row_num = 5
        lst = break_col( col, max_len, row_num )
        print( lst )

        assert len( lst ) == row_num
        assert lst == ['1234567, ', '12, 345, ', '12, ', '34567, ', '']


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


    def test__cls_to_tex( self ):

        # TODO
        return

        sym_lst = []
        for rank in range( 3, 9 + 1 ):
            for dpl in DPLattice.get_reduced_cls( rank, False ):
                lst1 = [Div( row ).mat_mul( dpl.M ) for row in sage_identity_matrix( rank ) ]
                for elt in lst1 + dpl.d_lst:
                    sym_lst += [   Div( elt.e_lst + ( 9 - len( elt.e_lst ) ) * [0] ) ]

        abc = 'abcdefghijklmnopqrstuvwxyz'
        ch_lst = []
        ch_lst += [ ch for ch in '012345678' + abc ]
        ch_lst += [ chr( ord( ch ) - 32 ) for ch in abc  ]
        ch_lst += [ '\\^' + ch for ch in abc  ]
        sym_lst = list( set( sym_lst ) )
        sym_lst.sort()
        e0 = Div( [1, 0, 0, 0, 0, 0, 0, 0, 0 ] )
        sym_lst.remove( e0 )
        sym_lst = [e0] + sym_lst
        legend = []
        dct = {}
        for i in range( len( sym_lst ) ):
            dct.update( {str( sym_lst[i] ):ch_lst[i]} )
            legend += [[ch_lst[i] + ':', ( '$' + str( sym_lst[i] ) + '$' ).replace( 'e', 'e_' ) ]]
        legend += [['', ''], ['', '']]




        out = ''
        out += 'A dictionary for symbols in the columns $A_\\sigma$ and $B$:\n\\\\\n'
        out += cls_to_tex( [], legend, [27], 3, 'l@{~}l' ).replace( '{@{}@{}c@{}|@{}c@{}|@{}c@{}}', '{@{}@{}c@{}@{}c@{}@{}c@{}}' )
        out += '\n\n'

        dct1 = {'A':'A_', 'D':'D_', 'E':'E_', '{':'\\underline{'}
        tab = []
        tab += [
            ['i  ', '$9$', "$A_0 $", '$A_0$', '$0$', '$1$', ''],
            7 * [''],
            ['ii ', '$8$', "$A_0 $", '$A_0$', '$0$', '$2$', ''],
            ['iii', '$8$', "$A_0 $", '$A_0$', '$0$', '$1$', ''],
            ['iv ', '$8$', "$A_0 $", '$A_0$', '$1$', '$1$', ''],
            ['v  ', '$8$', "$A_0 $", '$A_1$', '$0$', '$1$', '*'],
            7 * [''],
            ]
        idx = 0
        for rank in range( 3, 9 + 1 ):
            for dpl in DPLattice.get_reduced_cls( rank, False ):

                col1 = '$' + str( idx ) + '$'

                col2 = '$' + str( dpl.get_degree() ) + '$'

                col3 = '$' + str( dpl.get_marked_Mtype() ) + '$'
                for key in dct1:
                    col3 = str( col3 ).replace( key, dct1[key] )

                col4 = '$' + str( dpl.get_real_type() ) + '$'
                for key in dct1:
                    col4 = str( col4 ).replace( key, dct1[key] )

                col5 = '$' + str( dpl.get_numbers()[4] ) + '$'

                col6 = '$' + str( dpl.get_numbers()[5] ) + '$'

                lst1 = [ str( Div( rw ).mat_mul( dpl.M ) ) for rw in sage_identity_matrix( rank ) ]
                col7 = ''
                for elt in lst1: col7 += dct[elt]
                if col7 in ['012', '0123', '01234', '012345', '0123456', '01234567', '012345678']:
                    col7 = ''

                lst2 = [ str( d ) for d in dpl.d_lst ]
                col8 = '';
                for elt in lst2: col8 += dct[elt]


                if col4 in ['$7\underline{A_1}$', '$8\underline{A_1}$', '$4\underline{A_1}+\underline{D_4}$']:
                    col1 = '$\\times$'


                tab += [[col1, col2, col3, col4, col5, col6, col7 + '\#' + col8]]
                idx += 1
            if rank != 5:
                tab += [7 * ['']]

        # tab += 10 * [7 * ['']]

        #         i     d     A     B     E     G     AB
        hl = '@{~}l@{~~}l@{~~}l@{~~}l@{~~}l@{~~}l@{~~}l@{~}'
        out += cls_to_tex( ['', 'd', '$D(A)$', '$D(B)$', '$\#E$', '$\#G$', '$\sigma_A\#B$'], tab, [18, 18, 65, 65, 62, 62], 2, hl )

        out = '{\\tiny %\n' + out + '}\n'

        print( out )


if __name__ == '__main__':

    NSTools.filter( None )

    # TestConvertToTex().test__break_col()
    # TestConvertToTex().test__refine_table()
    TestConvertToTex().test__cls_to_tex()

#     from ns_lattice.dp_root_bases import get_graph
#
#     cls = DPLattice.get_reduced_cls( 9, False )
#     dlp = [c for c in cls if c.type == '4A2'][0]
#     print( dlp.get_real_type() )
#     print( dlp.d_lst )
#
#     print( dlp )
#
#     comp_lst = get_graph( dlp.d_lst ).connected_components()
#     comp_lst.reverse()  # smaller components first
#
#     for comp in comp_lst:
#         print( comp )


    pass
