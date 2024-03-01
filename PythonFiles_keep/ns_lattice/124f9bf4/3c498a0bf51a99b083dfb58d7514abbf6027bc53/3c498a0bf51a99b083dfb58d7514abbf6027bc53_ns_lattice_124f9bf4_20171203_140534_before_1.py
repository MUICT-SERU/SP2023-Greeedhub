'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 11, 2016
@author: Niels Lubbes

'''
import sys

from sage_interface import sage_ZZ
from sage_interface import sage_identity_matrix

from class_ns_tools import NSTools
from dp_root_bases import get_root_bases
from dp_root_bases import get_cls_root_bases
from dp_root_bases import get_dynkin_type
from dp_involutions import get_involutions
from dp_involutions import get_cls_involutions

from class_div import Div
from class_dp_lattice import DPLattice

from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries



def usecase__get_cls_root_bases( max_rank ):
    '''
    Obtain classification of root bases of root systems
    that have rank at most "max_ring". 
    See "dp_root_bases.get_cls_root_bases()".
    
    Parameters
    ----------
    max_rank : int
        Maximal rank for the root system in classification.    
    '''

    for rank in range( 3, max_rank + 1 ):

        d_lst_lst = get_cls_root_bases( max_rank )[rank]
        NSTools.p( 10 * '-' )
        i = 1
        for d_lst in d_lst_lst:
            NSTools.p( i, '<' + str( rank ) + '>', ': ', get_dynkin_type( d_lst ), '\t\t', d_lst )
            i += 1
        NSTools.p( '# =', len( d_lst_lst ) )


def usecase__get_tool_dct():
    '''    
    List current data in NSTools.get_tool_dct().
    '''

    # list keys
    for key in NSTools.get_tool_dct():
        NSTools.p( 'key =', key )

    # See "dp_root_bases.get_dynkin_type()".
    # for ( G, ts, t_lst ) in NSTools.get_tool_dct()['get_dynkin_type_4']:
    #    NSTools.p( ts, t_lst, G )


def usecase__get_root_bases( max_rank ):
    '''
    Prints the number of of all root bases for Neron-Severi lattices 
    of weak Del Pezzo surfaces, up to rank "max_rank".  
    
    See "dp_root_bases.get_root_bases()".
    
    Parameters
    ----------
    max_rank : int
        Maximal rank for the root system in classification.
    '''

    d_lst_lst = get_root_bases( max_rank )
    if False:
        for d_lst in d_lst_lst:
            NSTools.p( get_dynkin_type( d_lst ), '\t\t\t', d_lst )
    NSTools.p( 'number of all possible root bases = ', len( d_lst_lst ) )


def usecase__get_cls_involutions( max_rank ):
    '''
    Obtain classification of involutions so that the 
    associated root system is of rank at most "max_rank".
    
    See "dp_involutions.get_cls_involutions(max_rank)".
    
    Parameters
    ----------
    max_rank : int
        Maximal rank for the root system associated to involution in 
        classification.      
    '''

    # rank = rank of NS-lattice
    # M = matrix for involution
    # d_lst = basis for corresponding root subsystem

    invo_cls_dct = get_cls_involutions( max_rank )
    for rank in range( 3, max_rank + 1 ):
        NSTools.p( 10 * '-' )
        for ( M, d_lst ) in invo_cls_dct[rank]:

            NSTools.p( rank, get_dynkin_type( d_lst ), d_lst, list( M ) )

            # (h,e1,e2) |--> (?,?,?)
            b_lst = [Div( row ) for row in sage_identity_matrix( sage_ZZ, rank ).rows() ]
            NSTools.p( '\t', [b.mat_mul( M ).get_label( True ) for b in b_lst] )


def usecase__get_involutions( rank = 4, d_lst = [12], Mtype = 'A1' ):
    '''
    List all compatible involutions for a fixed root basis
    for singularities. The involution is required to preserve 
    the root bases for the singularities.
    
    Parameters
    ----------
    rank : int
        Rank for the root system of the singularities.
    d_lst : int[]
        Basis for the root system associated to the singularities.
    M_type : str
        Dynkin type of the root system of the involution.
    '''

    d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
    for ( M, Md_lst ) in get_involutions( rank ):

        # check whether involution M preserves d_lst
        dm_lst = [ d.mat_mul( M ) for d in d_lst ]
        if sorted( dm_lst ) != sorted( d_lst ):
            continue

        dpl = DPLattice.init( d_lst, Md_lst, M )
        if dpl.Mtype != Mtype:
            continue

        NSTools.p( dpl )

        k = Div( [-3] + ( rank - 1 ) * [1] )
        if k.mat_mul( M ) != k:
            raise Exception( 'The canonical class should be preserved M(k)=', k.mat_mul( M ) )


def usecase__get_cls_real_dp( max_rank ):
    '''
    List classification of real NS-lattices of weak Del Pezzo surfaces.

    See "DPLattice.get_cls_real_dp()".

    Parameters
    ----------
    max_rank : int
        Maximal rank for the root system associated to singularities and
        involutions of weak del Pezzo surfaces.
    '''
    # print all equivalence classes
    #
    dp_cls_dct = DPLattice.get_cls_real_dp( max_rank )
    for rank in range( 3, max_rank + 1 ):
        for dpl in dp_cls_dct[rank]:
            NSTools.p( dpl )

    # print out a table
    #
    NSTools.p( '(#families, degree ), involution, isolated singularities' )
    for rank in range( 3, max_rank + 1 ):
        for dpl in dp_cls_dct[rank]:
            NSTools.p( ( len( dpl.real_fam_lst ), dpl.get_degree() ), dpl.Mtype, dpl.type )


def usecase__get_cls_real_dp__celestials( max_rank ):
    '''
    Classification NS-lattices of surfaces with 
    at least two real families of circles and no real lines.
    
    See "DPLattice.get_cls_real_dp()".  
    
    Parameters
    ----------
    max_rank : int
        Maximal rank for the root system associated to singularities and
        involutions of weak     dp_cls_dct = DPLattice.get_cls_real_dp( max_rank )
    for rank in range( 3, max_rank + 1 ):
        for dpl in dp_cls_dct[rank]:
            NSTools.p( dpl )del Pezzo surfaces.    
    '''
    dp_cls_dct = DPLattice.get_cls_real_dp( max_rank )
    celestial_dct = {}
    table = []
    for rank in range( 3, max_rank + 1 ):
        for dpl in sorted( dp_cls_dct[rank] ):

            # no real lines and two families of conics
            if len( dpl.real_fam_lst ) >= 2 and len( dpl.real_m1_lst ) == 0:

                NSTools.p( dpl )

                if rank not in celestial_dct:
                    celestial_dct[rank] = []
                celestial_dct[rank] += [dpl]

                # determine whether there exists a family
                # pair with intersection product one.
                p1p1 = False
                for real_fam1 in dpl.real_fam_lst:
                    for real_fam2 in dpl.real_fam_lst:
                        if real_fam1 * real_fam2 == 1:
                            p1p1 = True

                table += [ [dpl.get_degree(), dpl.type, dpl.Mtype, p1p1] + [str( num ) for num in dpl.get_numbers()]]


    if table == []:
        NSTools.p( 'There exist no celestials for rank=' + str( rank ) + '...returning...' )
        return

    table = [['------'] * len( table[0] )] + table
    table = [['Degree', 'sing', 'real', 'P1xP1', '#(-2)', '#(-1)', '#(0)', '#RR(-2)', '#RR(-1)', '#RR(0)']] + table
    table = [['------'] * len( table[0] )] + table
    table += [['------'] * len( table[0] )]

    row_format = "{:<8}" * len( table[0] )
    for row in table:
        print( row_format.format( *row ) )

    for rank in celestial_dct:
        NSTools.p( 'deg =', 10 - rank, ' #lattice-classes =', len( celestial_dct[rank] ) )


def usecase__get_classes_dp1():
    '''
    Computes classes in the Neron-Severi lattice with
    of a degree 1 del Pezzo surface that predefined
    self-intersection and intersection with the 
    canonical class.
    '''

    # canonical class
    d = Div.new( '3e0-e1-e2-e3-e4-e5-e6-e7-e8' )

    dc = 2
    cc = 0
    NSTools.p( dc, cc )
    c_lst = get_div_set( d, dc, cc, False )
    for c in c_lst:
        NSTools.p( c.get_label() )

    dc = 2
    cc = 2
    NSTools.p( dc, cc )
    c_lst = get_div_set( d, dc, cc, False )
    for c in c_lst:
        NSTools.p( c.get_label() )

    dc = 2
    cc = 4
    NSTools.p( dc, cc )
    c_lst = get_div_set( d, dc, cc, False )
    for c in c_lst:
        NSTools.p( c.get_label() )



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



if __name__ == '__main__':

    #  Debug output settings
    #
    NSTools.filter( '__main__.py' )  # only print if output by module <file_name>
    NSTools.filter( None )

    NSTools.start_timer()

    #
    # Should be between 3 and 9.
    # computes classifications up to rank "max_rank".
    #
    max_rank = 6

    #########################################
    #                                       #
    # (Un)comment one or more use cases     #
    #                                       #
    #########################################

    # NSTools.get_tool_dct().pop( 'get_cls_root_bases_' + str( max_rank ), None )
    usecase__get_cls_root_bases( max_rank )

    usecase__get_tool_dct()
    usecase__get_root_bases( max_rank )
    # usecase__get_cls_involutions( max_rank )
    # usecase__get_involutions( max_rank, [12], 'A1' )
    # usecase__get_cls_real_dp( max_rank )
    # usecase__get_cls_real_dp__celestials( max_rank )
    # usecase__get_cls_real_dp__tex( max_rank )
    # if max_rank == 9:
    #    usecase__get_classes_dp1()  # takes a long time to terminate
    #    # usecase__circles()  # does not terminate within reasonable time


    #########################################
    #                                       #
    # End of list of use case methods.      #
    #                                       #
    #########################################

    NSTools.end_timer()
    print( '\nThe End' )



