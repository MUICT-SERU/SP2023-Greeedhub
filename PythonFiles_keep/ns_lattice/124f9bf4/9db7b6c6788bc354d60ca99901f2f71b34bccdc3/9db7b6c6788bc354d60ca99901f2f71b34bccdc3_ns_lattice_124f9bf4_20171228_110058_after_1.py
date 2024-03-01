'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 11, 2016
@author: Niels Lubbes

'''
import sys
import os

from sage_interface import sage_matrix
from sage_interface import sage_ZZ
from sage_interface import sage_identity_matrix
from sage_interface import sage_Subsets
from sage_interface import sage_Permutations
from sage_interface import sage_Graph

from class_ns_tools import NSTools

from class_div import Div

from div_in_lattice import get_divs
from div_in_lattice import get_ak

from class_dp_lattice import DPLattice

from ns_basis import get_bases_lst
from ns_basis import get_webs
from ns_basis import contains_perm
from ns_basis import nonreducible_webs
from ns_basis import nonreducible_intersect_webs

from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries

from convert_to_tex import table_to_tex


def usecase__circles():
    '''
    An example for how to compute circles on rational surface 
    
    Requires the linear_series package.
    '''

    # Blowup of projective plane in 3 colinear points
    # and 2 infinitly near points. The image of the
    # map associated to the linear series is a quartic
    # del Pezzo surface with 5 families of conics.
    # Moreover the surface contains 8 straight lines.
    #
    ring = PolyRing( 'x,y,z', True )
    p1 = ( -1, 0 )
    p2 = ( 0, 0 )
    p3 = ( 1, 0 )
    p4 = ( 0, 1 )
    p5 = ( 2, 0 )
    bp_tree = BasePointTree()
    bp_tree.add( 'z', p1, 1 )
    bp_tree.add( 'z', p2, 1 )
    bp_tree.add( 'z', p3, 1 )
    bp = bp_tree.add( 'z', p4, 1 )
    bp.add( 't', p5, 1 )
    ls = LinearSeries.get( 3, bp_tree )
    NSTools.p( ls.get_bp_tree() )
    NSTools.p( ls.get_implicit_image() )


    # compose map associated to linear series "ls"
    # with the inverse stereographic projection "Pinv".
    #
    R = PolynomialRing( QQ, 'y0,y1,y2,y3,y4,x,y,z' )
    y0, y1, y2, y3, y4, x, y, z = R.gens()
    delta = y1 ** 2 + y2 ** 2 + y3 ** 2 + y4 ** 2
    Pinv = [ y0 ** 2 + delta, 2 * y0 * y1, 2 * y0 * y2, 2 * y0 * y3, 2 * y0 * y4, -y0 ** 2 + delta]
    H = sage_eval( str( ls.pol_lst ), R.gens_dict() )
    PinvH = [ elt.subs( {y0:H[0], y1:H[1], y2:H[2], y3:H[3], y4:H[4]} ) for elt in Pinv ]
    NSTools.p( 'Pinv        =', Pinv )
    NSTools.p( 'H           =', H )
    NSTools.p( 'Pinv o H    =', PinvH )

    # In order to compute the NS-lattice of the image
    # of "PinvH" we do a base point analysis
    #
    #
    ls2 = LinearSeries( [str( elt ) for elt in PinvH], ring )
    NSTools.p( 'ls2         =', ls2.get_bp_tree() )


def usecase__get_tool_dct():
    '''    
    List keys in NSTools.get_tool_dct().
    '''

    # list keys
    for key in NSTools.get_tool_dct():
        NSTools.p( 'key =', key )


def usecase__get_cls_root_bases( max_rank ):
    '''
    Classification of root bases in root system of rank at most "max_rank".
    See "DPLattice.get_cls_root_bases()".
    
    Parameters
    ----------
    max_rank : int
        Maximal rank.  
    '''
    NSTools.p( 'Classification of root bases.' )

    for rank in range( 3, max_rank + 1 ):
        for dpl in DPLattice.get_cls_root_bases( rank ):
            print( str( rank ) + '\t' + dpl.type + '\t\t\t' + str( dpl.d_lst ) )
        print( 'total = ' + str( len( DPLattice.get_cls_root_bases( rank ) ) ) )


def usecase__get_reduced_cls_dp_lattice( max_rank, tex = False ):
    '''
    Classification NS-lattices of weak del Pezzo surfaces.  
    
    See "DPLattice.usecase__get_reduced_cls_dp_lattice()".  
    
    Parameters
    ----------
    max_rank : int
        Maximal rank for the root system associated to singularities and
        involutions of weak del Pezzo surfaces.
                    
    tex : bool
        If True, then output the classification as a table in Tex code.
    '''
    NSTools.p( 'Reduced classification of DPLattice objects.' )

    #
    # table 1
    #
    tab1 = []
    h1_lst = ['', 'deg', 'real', 'sing', '$\MbbP^1\\times\MbbP^1$',
              '\#(-2)', '\#(-1)', '\#(0)',
              '\#(-2)$_\MbbR$', '\#(-1)$_\MbbR$', '\#(0)$_\MbbR$']
    idx = 0
    for rank in range( 3, max_rank + 1 ):
        for dpl in DPLattice.get_reduced_cls( rank, False ):
            row = []
            row += [idx]
            row += [dpl.get_degree()]
            row += [dpl.Mtype]
            row += [dpl.type]
            if dpl.contains_fam_pair():
                row += ['y']
            else:
                row += ['n']
            row += dpl.get_numbers()

            tab1 += [row]
            idx += 1

    #
    # table 2
    #
    tab2 = []
    h2_lst = ['', 'deg', 'real', 'involution' ]
    idx = 0
    for rank in range( 3, max_rank + 1 ):
        for dpl in DPLattice.get_reduced_cls( rank, True ):
            div_tup = tuple( [Div( row ).mat_mul( dpl.M ) for row in sage_identity_matrix( rank ) ] )

            row = []
            row += [ idx ]
            row += [ dpl.get_degree() ]
            row += [ dpl.Mtype ]
            row += [ div_tup ]

            tab2 += [row]
            idx += 1

    #
    # table 3
    #
    tab3 = []
    h3_lst = ['', 'deg', 'real', 'sing', 'root base' ]
    idx = 0
    for rank in range( 3, max_rank + 1 ):
        for dpl in DPLattice.get_reduced_cls( rank, False ):

            row = []
            row += [idx]
            row += [dpl.get_degree()]
            row += [dpl.Mtype]
            row += [dpl.type]
            row += [[ d for d in dpl.d_lst ]]

            tab3 += [row]
            idx += 1

    #
    # ordering for the tables
    #
    tab_h_lst = [( tab2, h2_lst ), ( tab3, h3_lst ), ( tab1, h1_lst )]

    #
    # output the tables
    #
    if not tex:

        for tab, h_lst in tab_h_lst:

            num_cols = len( tab[0] )
            tab = [['------'] * num_cols] + tab
            tab = [h_lst] + tab
            tab = [['------'] * num_cols] + tab
            tab += [['------'] * num_cols]
            row_format = "{:<8}" * num_cols  # each column is 8 chars.

            for row in tab:
                print( row_format.format( *row ) )
            for rank in range( 3, max_rank + 1 ):
                print( 'deg =', 10 - rank, ' #lattice-classes =', len( DPLattice.get_reduced_cls( rank ) ) )

            print( 80 * '=' )

    else:

        #
        # parameters for table_to_tex()
        #
        max_len = 60
        row_num = 9
        replace_dct = {'A':'A_', 'D':'D_', 'E':'E_', 'e':'e_', '[':'\\{', ']':'\\}'}
        col_idx = 1

        s = ''
        for tab, h_lst in tab_h_lst:
            s += table_to_tex( h_lst, tab, replace_dct, col_idx, max_len, row_num )

        print( s )


def usecase__get_classes_dp1( rank ):
    '''
    Computes classes in the Neron-Severi lattice with
    predefined self-intersection and intersection with the 
    canonical class.
    
    Parameters
    ----------
    rank : int  
    '''

    # canonical class
    d = get_ak( rank )

    # basis change
    a_lst = [ 'e0-e1', 'e0-e2']
    a_lst = [ Div.new( a, rank ) for a in a_lst ]
    m1_lst = get_divs( d, 1, -1, True )
    print( d )
    M = sage_identity_matrix( rank )
    d_lst = []
    d_tup_lst = get_bases_lst( a_lst, M, d_lst, m1_lst, False )
    B = sage_matrix( sage_ZZ, [ dt.e_lst for dt in d_tup_lst[0] ] )

    # list the classes
    for ( dc, cc ) in [( 2, 0 ), ( 1, -1 ), ( 0, -2 ), ( 2, 2 ), ( 2, 4 ), ( 3, 1 )]:
        NSTools.p( '(dc, cc) =', ( dc, cc ) )
        c_lst = get_divs( d, dc, cc, False )
        for c in c_lst:
            NSTools.p( '\t\t', c, '\t\t', c.get_basis_change( B ) )


def usecase__get_webs( max_rank ):
    '''
    Compute hexagonal webs
    
    Parameters
    ----------
    max_rank : int  
    '''
    if False:
        d_lst = []
        Md_lst = []
        M = sage_identity_matrix( 6 )
        dpl = DPLattice( d_lst, Md_lst, M )
        print( dpl )

        table = get_webs( dpl )
        # https://docs.python.org/3/library/string.html
        row_format = "{:<17}" * len( table[0] )
        for row in table:
            print( row_format.format( *row ) )

        f_lst_lst = nonreducible_webs( dpl, 2, 3 )
        for f_lst in f_lst_lst:
            print( f_lst )


    numline = 1
    numfam = 3
    int_lst = [1]

    af_lst_lst = []
    for rank in range( 7, max_rank + 1 ):
        NSTools.p( 'rank =', rank )
        for dpl in DPLattice.get_cls_root_bases( rank ):
            f_lst_lst = nonreducible_intersect_webs( dpl, numline, numfam, int_lst )
            for f_lst in f_lst_lst:
                if not contains_perm( af_lst_lst, f_lst ):
                    af_lst_lst += [ f_lst ]
            NSTools.p( dpl )
            NSTools.p( 'f_lst_lst  =', len( f_lst_lst ), f_lst_lst )

    for af_lst in af_lst_lst:
        NSTools.p( af_lst[0].get_rank(), af_lst )
    NSTools.p( 'af_lst_lst  =', len( af_lst_lst ), af_lst_lst )


def usecase__graphs( rank ):
    '''
    M. Meringer: Fast Generation of Regular Graphs and Construction of Cages. Journal of Graph Theory 30, 137-146, 1999.
    '''
    rank = 7
    dpl = DPLattice.get_cls_root_bases( rank )[0]
    f_lst = dpl.real_fam_lst

    G = sage_Graph()
    G.add_vertices( range( len( f_lst ) ) )

    num_lst = []
    ne_lst = []  # each entry denotes the number of outgoing edges of some vertex
    for i in range( len( f_lst ) ):
        ne = 0
        for j in range( len( f_lst ) ):
            if f_lst[i] * f_lst[j] > 1:
                ne += 1
                num = f_lst[i] * f_lst[j]
                G.add_edge( i, j, num )
                if num not in num_lst:
                    num_lst += [num]

        if ne not in ne_lst:
            ne_lst += [ne]

    NSTools.p( 'labels      =', sorted( num_lst ) )  # [2,3,4,5,6,7,8]
    NSTools.p( 'regularity  =', sorted( ne_lst ) )  # E8: [2095]
    NSTools.p( 'vertices    =', len( f_lst ) )  # E8: [2160]


    P = G.graphplot( vertex_size = 1,
                     vertex_labels = True,
                     edge_labels = True,
                     color_by_label = False,
                     layout = 'circular' ).plot()

    P.save( os.environ['HOME'] + '/Documents/graph.png' )

    NSTools.p( '#components =', G.connected_components_number() )


if __name__ == '__main__':

    #  Debug output settings
    #
    # NSTools.filter( '__main__.py' )  # only print if output by module <file_name>
    NSTools.filter( None )
    # NSTools.get_tool_dct().clear()  # uncomment to remove all cache!

    # NSTools.start_timer()

    #
    # Should be between 3 and 9.
    # computes classifications up to rank "max_rank".
    #
    rank = 9

    #########################################
    #                                       #
    # (Un)comment one or more use cases     #
    #                                       #
    #########################################

    # usecase__get_tool_dct()
    # usecase__get_cls_root_bases( rank )
    # #usecase__get_reduced_cls_dp_lattice( rank, False )
    usecase__get_classes_dp1( rank )
    # usecase__get_webs( rank )
    # usecase__graphs( rank )
    # usecase__circles()  # does not terminate within reasonable time

    #########################################
    #                                       #
    # End of list of use case methods.      #
    #                                       #
    #########################################

    # NSTools.end_timer()
    # print( '\nThe End' )



