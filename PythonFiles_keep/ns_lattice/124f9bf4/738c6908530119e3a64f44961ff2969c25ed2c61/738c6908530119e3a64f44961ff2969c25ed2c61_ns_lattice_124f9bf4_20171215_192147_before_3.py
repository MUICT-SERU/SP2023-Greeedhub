'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Dec 14, 2017
@author: Niels Lubbes
'''

from sage_interface import sage_identity_matrix

from class_div import Div

from class_dp_lattice import DPLattice


def break_col( col, max_len, row_num ):
    '''
    Splits a string by commas in to a list of "row_num" substrings.
    The length of each substring should not exceed "max_len", if
    this is possible by splitting via commas.
    
    Parameters
    ----------
    col : int
    max_len : int
    row_num : int
    
    Returns
    -------
    list<string>        
    '''
    s_lst = str( col ).split( ',' )

    col_lst = []
    ts = ''
    for s in s_lst:
        ts += s + ', '
        if len( ts ) >= max_len:
            col_lst += [ts]
            ts = ''

    for i in range( row_num - len( col_lst ) ):
        col_lst += ['']

    return col_lst


def refine_table( table, max_len = 50, row_num = 5 ):
    '''
    Break a long row into several short rows
    
    Parameters
    ----------
    row : list<list<object>>
    
    Returns
    -------
    list<list<object>>    
    '''
    new_table = []
    for ri in range( len( table ) ):
        for i in range( row_num ):

            new_row = []
            for ci in range( len( table[ri] ) ):
                new_row += [ break_col( table[ri][ci], max_len, row_num )[i] ]
            if set( new_row ) != {''}:
                new_table += [new_row]

    return new_table


def get_table_header( h_lst ):
    '''
    Parameters
    ----------
    h_lst : list<object>
    
    Returns
    -------
    string
        Table header in Tex.
    '''

    h_str = ''
    h_str += '\n' + '\\begin{center}'
    h_str += '\n' + '{\\tiny'
    h_str += '\n' + '\\begin{longtable}{|c|c|c|c|c|c|c|c|c|c|c|}'
    h_str += '\n' + '\\hline'
    h_str += '\n'
    for h in h_lst:
        h_str += str( h ) + '&'
    h_str = h_str[:-1]
    h_str += '\n' + '\\\\\\hline\\hline\\endhead'



def get_table_footer():
    '''
    Returns
    -------
    string
        Table footer in Tex.
    '''
    f_str = ''
    f_str += '\n' + '\\end{longtable}'
    f_str += '\n' + '}'
    f_str += '\n' + '\\end{center}'
    return f_str


def table_to_tex( table, replace_dct = {}, col_idx = -1 ):
    '''
    Parameters
    ----------
    table : list<list<object>>
    
    replace_dct : dict<string:string>
        A dictionary whose keys and values are strings.
    
    col_idc : int
        index of a column
    
    Returns
    -------
    string
        A string representing the input table in Tex.
    '''
    out = '\n'
    if table == []:
        return ''
    prev_row = table[0]
    for row in table:
        if row[col_idx] != prev_row[col_idx]:
            out += '\\hline' + '\n'
        for col in row:
            for key in replace_dct:
                col = str( col ).replace( key, replace_dct[key] )
            out += str( col ) + ' &'
        out = out[:-1]
        out += '\\' + '\\' + '\\hline' + '\n'
    return out


def dp_lattice_tex():
    max_rank = 9

    dpl_dct = {}
    dpl_dct[3] = DPLattice.get_cls_real_dp( 3 )
    dpl_dct[4] = DPLattice.get_cls_real_dp( 4 )
    dpl_dct[5] = DPLattice.get_cls_real_dp( 5 )
    dpl_dct[6] = DPLattice.get_cls_real_dp( 6 )
    dpl_dct[7] = DPLattice.get_cls_real_dp( 7 )
    dpl_dct[8] = DPLattice.get_cls_root_bases( 8 )
    dpl_dct[9] = DPLattice.get_cls_root_bases( 9 )


    max_len = 50
    row_num = 5
    dct = {'A':'A_', 'D':'D_', 'E':'E_', 'e':'e_'}

    #
    # table 1
    #
    tab1 = []
    h1_lst = ['', 'deg', 'real', 'sing', '$\MbbP^1\\times\MbbP^1$',
              '\#(-2)', '\#(-1)', '\#(0)',
              '\#(-2)$_\MbbR$', '\#(-1)$_\MbbR$', '\#(0)$_\MbbR$']
    idx = 0
    for rank in range( 3, max_rank + 1 ):
        for dpl in dpl_dct[rank]:
            row = []
            row += [idx]
            row += [dpl.get_degree()]
            row += [dpl.Mtype]
            row += [dpl.type]
            if dpl.contains_fam_pair():
                row += ['\\text{yes}']
            else:
                row += ['\\text{no}']
            row += dpl.get_numbers()
            tab1 += [row]

    #
    # table 2
    #
    tab2 = []
    h2_lst = ['', 'deg', 'real', 'involution' ]
    idx = 0
    for rank in range( 3, max_rank + 1 ):
        for dpl in DPLattice.get_cls_involutions( rank ):
            div_tup = tuple( [Div( row ).mat_mul( dpl.M ) for row in sage_identity_matrix( rank ) ] )

            row = []
            row += [ idx ]
            row += [ dpl.get_degree() ]
            row += [ dpl.Mtype ]
            row += [ div_tup ]

            tab2 += [row]

    #
    # table 3
    #
    tab2 = []
    h3_lst = ['', 'deg', 'real', 'sing', 'root base' ]
    idx = 0
    for rank in range( 3, max_rank + 1 ):
        for dpl in dpl_dct[rank]:

            row = []
            row += [idx]
            row += [dpl.get_degree()]
            row += [dpl.Mtype]
            row += [dpl.type]
            row += [[ d for d in dpl.d_lst ]]

            tab3 += [row]


    s = ''

    s += '\n\n\\subsection{}'
    s += get_table_header( h1_lst )
    s += table_to_tex( refine_table( tab1, max_len, row_num ), dct, 1 )
    s += get_table_footer()

    s += '\n\n\\subsection{}'
    s += get_table_header( h2_lst )
    s += table_to_tex( refine_table( tab2, max_len, row_num ), dct, 1 )
    s += get_table_footer()

    s += '\n\n\\subsection{}'
    s += get_table_header( h3_lst )
    s += table_to_tex( refine_table( tab3, max_len, row_num ), dct, 1 )
    s += get_table_footer()

    return s

