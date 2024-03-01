'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.

Created on Aug 11, 2016

@author: Niels Lubbes
'''

from sage.all import *

from div_set import *
from dp_involutions import *
from dp_root_bases import *
from ns_basis import *

from class_ns_tools import NSTools
from class_div import Div
from class_dp_lattice import DPLattice


# from linear_series.class_poly_ring import PolyRing
# from linear_series.class_base_points import BasePointTree
# from linear_series.class_linear_series import LinearSeries


nt = NSTools()


def usecase__get_cls_root_bases( max_rank ):
    '''
    Obtain classification of root bases of rank at most "max_rank".
    
    See "dp_root_bases.get_cls_root_bases(max_rank)".
    '''

    for rank in range( 3, max_rank + 1 ):
        d_lst_lst = get_cls_root_bases( max_rank )[rank]
        nt.p( 10 * '-' )
        i = 1
        for d_lst in d_lst_lst:
            nt.p( i, '<' + str( rank ) + '>', ': ', get_dynkin_type( d_lst ), '\t\t', d_lst )
            i += 1
        nt.p( '# =', len( d_lst_lst ) )


def usecase__get_tool_dct():
    '''    
    List current data in NSTools.get_tool_dct().
    '''

    # list keys
    for key in nt.get_tool_dct():
        nt.p( 'key =', key )

    # See "dp_root_bases.get_dynkin_type()".
    for ( G, ts, t_lst ) in nt.get_tool_dct()['get_dynkin_type_4']:
        nt.p( ts, t_lst, G )


def usecase__get_root_bases( max_rank ):
    '''
    Compute all root bases for Neron-Severi lattices 
    of weak Del Pezzo surfaces, up to rank "max_rank".  
    
    See "dp_root_bases.get_root_bases()".
    '''
    bnd_max_rank = min( max_rank, 6 )
    d_lst_lst = get_root_bases( bnd_max_rank )
    if False:
        for d_lst in d_lst_lst:
            nt.p( get_dynkin_type( d_lst ), '\t\t\t', d_lst )
    nt.p( 'number of all possible root bases = ', len( d_lst_lst ) )


def usecase__cls_root_bases( max_rank ):
    '''
    Compute classification of 
    root bases up to rank "max_rank".  
    
    See "dp_root_bases.get_cls_root_bases()".
    '''

    for d_lst in get_cls_root_bases( max_rank ):
        nt.p( get_dynkin_type( d_lst ), '\t\t\t', d_lst )


def usecase__get_cls_involutions( max_rank ):
    '''
    Obtain classification of involutions.
    
    See "dp_involutions.get_cls_involutions(max_rank)".
    '''

    # rank = rank of NS-lattice
    # M = matrix for involution
    # d_lst = basis for corresponding root subsystem

    invo_cls_dct = get_cls_involutions( max_rank )
    for rank in range( 3, max_rank + 1 ):
        nt.p( 10 * '-' )
        for ( M, d_lst ) in invo_cls_dct[rank]:

            nt.p( rank, get_dynkin_type( d_lst ), d_lst, list( M ) )

            # (h,e1,e2) |--> (?,?,?)
            b_lst = [Div( row ) for row in identity_matrix( ZZ, rank ).rows() ]
            nt.p( '\t', [b.mat_mul( M ).get_label( True ) for b in b_lst] )


def usecase__get_involutions():
    '''
    List all compatible involutions for a fixed root basis.
    '''

    rank = 6  # rank of NS-lattice
    # d_lst = [12, 34]  # root basis
    d_lst = []
    Mtype = 'D4'  # root system corresponding to involution is of this type

    d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
    for ( M, Md_lst ) in get_involutions( rank ):

        # check whether involution M preserves d_lst
        dm_lst = [ d.mat_mul( M ) for d in d_lst ]
        if sorted( dm_lst ) != sorted( d_lst ):
            continue

        dpl = DPLattice.init( d_lst, Md_lst, M )
        if dpl.Mtype != Mtype:
            continue

        nt.p( dpl )

        k = Div( [-3] + ( rank - 1 ) * [1] )
        if k.mat_mul( M ) != k:
            raise Exception( 'The canonical class should be preserved M(k)=', k.mat_mul( M ) )


def usecase__get_cls_real_dp( max_rank ):
    '''
    Classify real NS-lattices of weak Del Pezzo surfaces
    
    See "DPLattice.get_cls_real_dp()".
    '''
    bnd_max_rank = min( max_rank, 7 )
    nt.p( 'max_rank =', max_rank )

    # print all equivalence classes
    #
    dp_cls_dct = DPLattice.get_cls_real_dp( bnd_max_rank )
    for rank in range( 3, bnd_max_rank + 1 ):
        for dpl in dp_cls_dct[rank]:
            nt.p( dpl )

    # print out a formatted table
    #
    for rank in range( 3, bnd_max_rank + 1 ):
        for dpl in dp_cls_dct[rank]:
            # (#families, degree ), involution, isolated singularities
            nt.p( ( len( dpl.real_fam_lst ), dpl.get_degree() ), dpl.Mtype, dpl.type )


def usecase__get_cls_real_dp__celestials( max_rank ):
    '''
    Classification NS-lattices of surfaces with 
    at least 2 real families of circles and no real lines.
    
    See "DPLattice.get_cls_real_dp()".  
    '''
    bnd_max_rank = min( max_rank, 7 )

    dp_cls_dct = DPLattice.get_cls_real_dp( bnd_max_rank )
    celestial_dct = {}
    table = []
    for rank in range( 3, bnd_max_rank + 1 ):
        for dpl in sorted( dp_cls_dct[rank] ):
            # no real lines and two families of conics
            if len( dpl.real_fam_lst ) >= 2 and len( dpl.real_m1_lst ) == 0:

                nt.p( dpl )

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


    table = [['------'] * len( table[0] )] + table
    table = [['Degree', 'sing', 'real', 'P1xP1', '#(-2)', '#(-1)', '#(0)', '#RR(-2)', '#RR(-1)', '#RR(0)']] + table
    table = [['------'] * len( table[0] )] + table
    table += [['------'] * len( table[0] )]

    row_format = "{:<8}" * len( table[0] )
    for row in table:
        print( row_format.format( *row ) )

    for rank in celestial_dct:
        nt.p( 'deg =', 10 - rank, ' #lattice-classes =', len( celestial_dct[rank] ) )


def usecase__get_cls_real_dp__tex( max_rank ):
    '''
    We construct a Tex string for a table with 
    a classification of celestials.
    '''
    bnd_max_rank = min( max_rank, 7 )

    dp_cls_dct = DPLattice.get_cls_real_dp( bnd_max_rank )
    celestial_dct = {}
    for rank in range( 3, bnd_max_rank + 1 ):
        for dpl in sorted( dp_cls_dct[rank] ):
            if len( dpl.real_fam_lst ) >= 2 and len( dpl.real_m1_lst ) == 0:
                if rank not in celestial_dct:
                    celestial_dct[rank] = []
                celestial_dct[rank] += [dpl]

    print( DPLattice.get_tex_table( celestial_dct ) )


def usecase__circles():
    '''
    An example for how to compute circles on rational surface 
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


def usecase__bases():
    '''
    Compute bases for NS-lattice.
    '''


def usecase__conjecture():
    '''
    Try to find counter examples for the following 
    conjecture:
    
    Real minimal families that are not minimal over 
    the complex numbers form complete linear series 
    of dimension at most three.
    '''

    rnk_bound = 10
    h0_bound = 10
    hi_bound = 5
    ff_bound = 5


    for rnk in range( 3, rnk_bound ):
        for h0 in range( 2, h0_bound ):
            S = Subsets( ( rnk - 1 ) * range( hi_bound ), rnk - 1, submultiset = True )
            for h_lst in S:
                h_lst.reverse()
                h_lst = [h0] + [-h for h in h_lst]
                if h_lst[1] == 0 or h_lst[1] != h_lst[2]:
                    continue

                h = Div( h_lst )
                k = Div( [-3] + ( rnk - 1 ) * [1] )
                if h * h < 0 or h * h - h * k < 6:
                    continue

                mindeg = None
                for hf in range( 1, h[0] + 1 ):
                    if mindeg != None:
                        continue
                    f_lst = []
                    for ff in range( 0, ff_bound ):
                        # NSTools.set_enable_tool_dct( False )
                        f_lst = get_div_set( h, hf, ff, True )
                        # NSTools.set_enable_tool_dct( True )
                        # print( h, hf, ff, f_lst )
                        f_lst = [f for f in f_lst if f[1] == f[2] ]
                        if len( f_lst ) > 0:
                            NSTools.p( 'h=', h, ', hh=', h * h, ', hf=', hf, ', ff=', ff, ', len(f_lst)=', len( f_lst ) )
                            for f in f_lst:
                                NSTools.p( '\t\t', f )
                            mindeg = hf



if __name__ == '__main__':

    #  Debug output settings
    #
    nt.filter( '__main__.py' )  # only print if output by module <file_name>
    # nt.filter( None )
    nt.start_timer()

    #
    # Should be between 3 and 9.
    # computes classifications up to rank "max_rank".
    # If max_rank==9 then the computations take about 4 hours.
    #
    max_rank = 4

    #########################################
    #                                       #
    # (Un)comment one or more use cases     #
    #                                       #
    #########################################

    # usecase__get_cls_root_bases( max_rank )
    # usecase__get_tool_dct()
    # usecase__get_root_bases( max_rank )
    # usecase__get_cls_root_bases( max_rank )
    # usecase__get_cls_involutions( max_rank )
    # usecase__get_involutions()
    # usecase__get_cls_real_dp( max_rank )
    # usecase__get_cls_real_dp__celestials( max_rank )
    # usecase__get_cls_real_dp__tex( max_rank )
    # usecase__circles()
    usecase__conjecture()

    #########################################
    #                                       #
    # End of list of use case methods.      #
    #                                       #
    #########################################

    # end timing
    nt.end_timer()

    print()
    print( 'The End' )



