'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Dec 14, 2017
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_identity_matrix

from ns_lattice.class_div import Div

from ns_lattice.class_dp_lattice import DPLattice

from ns_lattice.class_ns_tools import NSTools


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

    col = str( col )

    col_lst = []
    if ',' not in col or len( col ) < max_len:
        col_lst = [ str( col ) ]
    else:
        s_lst = str( col ).split( ',' )
        ts = ''
        for s in s_lst:

            if len( ts + s + ', ' ) >= max_len:
                col_lst += [ts]
                ts = ''

            ts += s + ', '
            if ts[-3:] in ['), ', '], ']:
                ts = ts[:-2]  # remove the comma at the end

        # add remainder
        col_lst += [ts]

    # we cannot break up a column in too many rows
    if row_num - len( col_lst ) < 0:
        raise Exception( 'Parameter row_num is too small: ', row_num, '<', len( col_lst ) )

    # return row_num columns
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
                # NSTools.p( table[ri][ci], new_row, break_col( table[ri][ci], max_len, row_num ) )
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
    h_str += '\n' + '\\begin{longtable}{|' + ( len( h_lst ) * 'c|' ) + '}'
    h_str += '\n' + '\\hline'
    h_str += '\n'
    for h in h_lst:
        h_str += str( h ) + '&'
    h_str = h_str[:-1]
    h_str += '\n' + '\\\\\\hline\\hline\\endhead'
    return h_str


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


def table_to_tex( h_lst, table, replace_dct = {}, col_idx = -1, max_len = 60, row_num = 10 ):
    '''
    Parameters
    ----------
    h_lst : list<string>
        A list of string defining the column 
        headers of a table.
    
    table : list<list<object>>
        A list of lists represent rows in a table.
    
    replace_dct : dict<string:string>
        A dictionary whose keys and values are strings.
    
    col_idx : int
        Index of a column.
    
    Returns
    -------
    string
        A string representing "table" in Tex format.
        The column headers are defined by "h_lst".
        The characters in each column entry are adapted using
        dictionary "replace_dct" so that key is replaced with value.  
        If the "col_idx"-th column changes at the subsequent row,
        then a horizontal line separator is added. 
        If a column entry is longer than "max_len" characters, 
        then then it is broken up in several rows, by the splitting 
        the string with respect to the comma.         
    '''
    out = ''
    out += get_table_header( h_lst )

    # split columns that are too long in several rows
    table = refine_table( table, max_len, row_num )

    # construct tex string for each row in table
    prv_val = '' if col_idx == -1 else table[0][col_idx]
    for row in table:

        # Check whether to add a horizontal separator line in table.
        # We take in account that a row may be split up in several rows.
        cur_val = '' if col_idx == -1 else row[col_idx]
        if cur_val == '':
            cur_val = prv_val
        if cur_val != prv_val:
            out += '\\hline' + '\n'
        prv_val = cur_val

        # tex code for row
        for col in row:

            # replace characters in column string
            for key in replace_dct:
                col = str( col ).replace( key, replace_dct[key] )

            # tex code for a column
            out += '$' + str( col ) + ' $' + ' &'

        # omit the last &-separator
        out = out[:-1]

        # tex code for ending a table row
        out += '\\' + '\\' + '\\hline' + '\n'

    # add footer for table in the end
    out += get_table_footer()
    return out
