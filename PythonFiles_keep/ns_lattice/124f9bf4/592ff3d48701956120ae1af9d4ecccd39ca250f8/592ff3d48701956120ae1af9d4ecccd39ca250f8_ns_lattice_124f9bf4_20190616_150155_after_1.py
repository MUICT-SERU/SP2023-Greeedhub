'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 11, 2016
@author: Niels Lubbes
'''

import sys
import os

from ns_lattice.sage_interface import sage_matrix
from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_Subsets
from ns_lattice.sage_interface import sage_Permutations
from ns_lattice.sage_interface import sage_Graph
from ns_lattice.sage_interface import sage_gcd
from ns_lattice.sage_interface import sage_factor

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_div import Div

from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_ak

from ns_lattice.class_dp_lattice import DPLattice

from ns_lattice.ns_basis import get_bases_lst

from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries


def usecase__get_cls( max_rank ):
    '''
    Classification of root bases in root system of rank at most "max_rank".
    See "DPLattice.get_cls_root_bases()".
    
    Parameters
    ----------
    max_rank : int
        Maximal rank.  
    '''
    s = ''
    for rank in range( 3, max_rank + 1 ):
        for dpl in DPLattice.get_cls( rank ):
            s += str( rank ) + '\t'
            s += dpl.get_marked_Mtype() + '\t'
            s += dpl.get_real_type() + '\t'
            s += dpl.get_numbers() + '\t'
            s += '\n'
        s += 80 * '-' + '\n'

    NSTools.p( 'Classification of root bases:\n' + s )


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


def usecase__graphs( rank ):
    '''
    M. Meringer: Fast Generation of Regular Graphs and Construction of Cages. Journal of Graph Theory 30, 137-146, 1999.
    '''
    rank = 7
    dpl = DPLattice.get_cls( rank )[0]
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

    P.save( os.environ['OUTPUT_PATH'] + 'graph.png' )

    NSTools.p( '#components =', G.connected_components_number() )


def usecase__construct_surfaces():
    '''
    We construct a surface parametrization and its Neron-Severi lattice. 
     
    Requires the linear_series package.
    '''

    # Blowup of projective plane in 3 colinear points
    # and 2 infinitely near points. The image of the
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
    ls = LinearSeries.get( [3], bp_tree )
    NSTools.p( ls.get_bp_tree() )
    NSTools.p( 'implicit equation =\n\t', ls.get_implicit_image() )

    # construct NS-lattice where p1=e1,...,p5=e5
    rank = 6
    d_lst = [ 'e0-e1-e2-e3', 'e4-e5' ]  # basepoint p5 is infinitely near to p4
    Md_lst = []
    M = sage_identity_matrix( 6 )
    d_lst = [ Div.new( d, rank ) for d in d_lst ]
    Md_lst = [ Div.new( Md, rank ) for Md in Md_lst ]
    M = sage_matrix( M )
    dpl = DPLattice( d_lst, Md_lst, M )
    NSTools.p( 'Neron-Severi lattice =', dpl )

    # search representative for the equivalence class in classification
    assert dpl in DPLattice.get_cls( rank )


def usecase__roman_circles():
    '''
    We compute circles on a Roman surface.
    '''
    # parametrization of the Roman surface
    #
    p_lst = '[ z^2+x^2+y^2, -z*x, -x*y, z*y ]'

    # we consider the stereographic projection from
    #     S^3 = { x in P^4 | -x0^2+x1^2+x2^2+x3^2+x4^2 = 0 }
    # where the center of projection is (1:0:0:0:1):
    #     (x0:x1:x2:x3:x4) |---> (x0-x4:x1:x2:x3)

    # inverse stereographic projection into 3-sphere
    #
    s_lst = '[ y0^2+y1^2+y2^2+y3^2, 2*y0*y1, 2*y0*y2, 2*y0*y3, -y0^2+y1^2+y2^2+y3^2 ]'

    # compose p_lst with s_lst
    #
    ring = PolyRing( 'x,y,z,y0,y1,y2,y3' )
    x, y, z, y0, y1, y2, y3 = ring.gens()
    p_lst = ring.coerce( p_lst )
    s_lst = ring.coerce( s_lst )
    dct = { y0:p_lst[0], y1:p_lst[1], y2:p_lst[2], y3:p_lst[3] }
    sp_lst = [ s.subs( dct ) for s in s_lst ]
    NSTools.p( 'sp_lst =' )
    for sp in sp_lst: NSTools.p( '\t\t', sage_factor( sp ) )
    NSTools.p( 'gcd(sp_lst) =', sage_gcd( sp_lst ) )

    # determine base points
    #
    ring = PolyRing( 'x,y,z', True )
    sp_lst = ring.coerce( sp_lst )
    ls = LinearSeries( sp_lst, ring )
    NSTools.p( ls.get_bp_tree() )

    # We expect that the basepoints come from the intersection
    # of the Roman surface with the absolute conic:
    #    A = { (y0:y1:y2:y3) in P^3 | y0=y1^2+y2^2+y3^2 = 0 }
    #
    # Circles are the image via p_lst of lines that pass through
    # complex conjugate points.
    #
    ring = PolyRing( 'x,y,z', False )  # reinitialize ring with updated numberfield
    a0, a1, a2, a3 = ring.root_gens()

    # a0=(1-I*sqrt(3)) with conjugate a0-1 and minimal polynomial t^2-t+1

    # we compute candidate classes of circles
    #
    h = Div.new( '4e0-e1-e2-e3-e4-e5-e6-e7-e8' )
    div_lst = get_divs( h, 2, -2, False ) + get_divs( h, 2, -1, False )
    NSTools.p( 'Classes of circles up to permutation:' )
    for c in div_lst:
        NSTools.p( '\t\t', c )

    # We recover the preimages of circles in the Roman surface
    # under the map p_lst, by constructing for each candidate
    # class the corresponding linear series.

    # 2e0-e1-e2-e3-e4-e5-e6-e7-e8
    b = [( a0 - 1, -a0 ), ( -a0, a0 - 1 )]
    b += [( -a0 + 1, a0 ), ( a0, -a0 + 1 )]
    b += [ ( a0 - 1, a0 ), ( -a0, -a0 + 1 )]
    b += [( -a0 + 1, -a0 ), ( a0, a0 - 1 )]
    bp_tree = BasePointTree()
    for i in range( 6 ):
        bp_tree.add( 'z', b[i], 1 )
    NSTools.p( 'basepoints =', b )
    NSTools.p( LinearSeries.get( [2], bp_tree ) )

    # e0-e1-e2
    b = [( a0 - 1, -a0 ), ( -a0, a0 - 1 )]
    bp_tree = BasePointTree()
    bp = bp_tree.add( 'z', b[0], 1 )
    bp = bp_tree.add( 'z', b[1] , 1 )
    NSTools.p( 'basepoints =', b )
    NSTools.p( LinearSeries.get( [1], bp_tree ) )

    # e0-e3-e4
    b = [( -a0 + 1, a0 ), ( a0, -a0 + 1 )]
    bp_tree = BasePointTree()
    bp = bp_tree.add( 'z', b[0], 1 )
    bp = bp_tree.add( 'z', b[1] , 1 )
    NSTools.p( 'basepoints =', b )
    NSTools.p( LinearSeries.get( [1], bp_tree ) )

    # e0-e5-e6
    b = [ ( a0 - 1, a0 ), ( -a0, -a0 + 1 )]
    bp_tree = BasePointTree()
    bp = bp_tree.add( 'z', b[0], 1 )
    bp = bp_tree.add( 'z', b[1] , 1 )
    NSTools.p( 'basepoints =', b )
    NSTools.p( LinearSeries.get( [1], bp_tree ) )

    # e0-e7-e8
    b = [( -a0 + 1, -a0 ), ( a0, a0 - 1 )]
    bp_tree = BasePointTree()
    bp = bp_tree.add( 'z', b[0], 1 )
    bp = bp_tree.add( 'z', b[1] , 1 )
    NSTools.p( 'basepoints =', b )
    NSTools.p( LinearSeries.get( [1], bp_tree ) )

    return


if __name__ == '__main__':

    #  Debug output settings
    #
    mod_lst = []
    mod_lst += ['__main__.py']
    mod_lst += ['class_dp_lattice.py']
    mod_lst += ['class_eta.py']
    NSTools.filter( mod_lst )  # output only from specified modules
    # NSTools.filter( None )  # print all verbose output, comment to disable.
    # NSTools.get_tool_dct().clear()  # uncomment to remove all cache!

    if 'OUTPUT_PATH' not in os.environ:
        os.environ['OUTPUT_PATH'] = './'

    NSTools.start_timer()

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

    usecase__get_cls( rank )
    # usecase__get_classes_dp1( rank )
    # usecase__graphs( rank )
    # usecase__construct_surfaces()
    # usecase__roman_circles()  # takes about 3 minutes

    #########################################
    #                                       #
    # End of list of use case methods.      #
    #                                       #
    #########################################

    NSTools.end_timer()
    NSTools.p( 'The End' )



