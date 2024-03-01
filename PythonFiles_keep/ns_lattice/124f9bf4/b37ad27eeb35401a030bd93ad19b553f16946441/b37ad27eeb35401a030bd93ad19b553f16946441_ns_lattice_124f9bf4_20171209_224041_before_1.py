'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 11, 2016
@author: Niels Lubbes

'''
import sys

from sage_interface import sage_identity_matrix
from sage_interface import sage_Subsets
from sage_interface import sage_Permutations

from class_ns_tools import NSTools

from class_div import Div

from div_in_lattice import get_divs
from div_in_lattice import get_ak

from class_dp_lattice import DPLattice

from ns_basis import get_webs

from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries




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


def usecase__get_cls_real_dp( max_rank, celestial = False ):
    '''
    Classification NS-lattices of weak del Pezzo surfaces.  
    If celestial==True, then only surfaces with 
    at least two real families of circles and no real lines
    are listed.
    
    See "DPLattice.get_cls_real_dp()".  
    
    Parameters
    ----------
    max_rank : int
        Maximal rank for the root system associated to singularities and
        involutions of weak del Pezzo surfaces.
    
    celestial : bool
        Determines whether to classify only celestials.
    '''
    NSTools.p( 'Classification of DPLattice objects. celestial =', celestial )

    celestial_dct = {}
    table = []
    for rank in range( 3, max_rank + 1 ):
        for dpl in DPLattice.get_cls_real_dp( rank ):

            # no real lines and two families of conics
            if celestial and ( len( dpl.real_fam_lst ) < 2 or len( dpl.real_m1_lst ) != 0 ):
                continue

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

            table += [ [dpl.get_degree(), dpl.Mtype, dpl.type, p1p1] + [str( num ) for num in dpl.get_numbers()]]


    if table == []:
        NSTools.p( 'There exist no celestials for rank=' + str( rank ) + '...returning...' )
        return

    table = [['------'] * len( table[0] )] + table
    table = [['Degree', 'real', 'sing', 'P1xP1', '#(-2)', '#(-1)', '#(0)', '#RR(-2)', '#RR(-1)', '#RR(0)']] + table
    table = [['------'] * len( table[0] )] + table
    table += [['------'] * len( table[0] )]

    row_format = "{:<8}" * len( table[0] )
    for row in table:
        print( row_format.format( *row ) )

    for rank in celestial_dct:
        print( 'deg =', 10 - rank, ' #lattice-classes =', len( celestial_dct[rank] ) )


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

    for ( dc, cc ) in [( 2, 0 ), ( 1, -1 ), ( 0, -2 ), ( 2, 2 ), ( 2, 4 ), ( 3, 1 )]:
        NSTools.p( '(dc, cc) =', ( dc, cc ) )
        c_lst = get_divs( d, dc, cc, False )
        for c in c_lst:
            NSTools.p( '\t\t', c.get_label() )


def usecase__get_webs( rank ):
    '''
    Compute hexagonal webs
    
    Parameters
    ----------
    rank : int  
    '''
    if False:

        dpl_lst = DPLattice.get_cls_real_dp( 6 )
        for dpl in dpl_lst:
            if dpl.Mtype == '2A1' and dpl.type == 'A0' and len( dpl.real_fam_lst ) == 6:
                print( dpl )
                print( dpl.d_lst )
                print( dpl.Md_lst )
                print( list( dpl.M ) )
        sys.exit()

    # ring torus
    # dpl.Mtype == '2A1' and dpl.type == '4A1' and len( dpl.real_fam_lst ) == 4:
    # ----
    # d_lst = [ Div.new( d, 6 ) for d in ['e2-e4', 'e3-e5', 'e0-e1-e2-e4', 'e0-e1-e3-e5'] ]
    # Md_lst = [ Div.new( d, 6 ) for d in ['e4-e5', 'e0-e1-e2-e3'] ]
    # M = sage_matrix( sage_ZZ, [( 2, 1, 1, 1, 0, 0 ), ( -1, 0, -1, -1, 0, 0 ), ( -1, -1, 0, -1, 0, 0 ), ( -1, -1, -1, 0, 0, 0 ), ( 0, 0, 0, 0, 0, 1 ), ( 0, 0, 0, 0, 1, 0 )] )
    # dpl = DPLattice( d_lst, Md_lst, M )

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

    ak = get_ak( 6 )
    web_lst = []
    for trip in sage_Subsets( range( len( table[0] ) ), 3 ):
        for row in table:
            fa = row[ trip[0] ].e_lst[0]
            fb = row[ trip[1] ].e_lst[0]
            fc = row[ trip[2] ].e_lst[0]
            if fa == fb == fc == 1:
                newweb = [ table[0][trip[i]] for i in range( 3 )]

                found = False
                for perm in sage_Permutations( range( 5 ) ):
                    permweb = [ Div( [d[0]] + [ d[i + 1] for i in perm ], d.rank() ) for d in newweb ]
                    for web in web_lst:
                        if set( web ) == set( permweb ):
                            found = True
                            break
                    if found:
                        break

                if not found:
                    web_lst += [newweb]
    print( ' --- ' )
    for web in web_lst:
        print( web )

    noweb_lst = []
    for trip in sage_Subsets( range( len( table[0] ) ), 3 ):
        noweb = [ table[0][trip[i]] for i in range( 3 )]
        found = False
        for perm in sage_Permutations( range( 5 ) ):
            permweb = [ Div( [d[0]] + [ d[i + 1] for i in perm ], d.rank() ) for d in noweb ]
            for web in web_lst:
                if set( web ) == set( permweb ):
                    found = True
                    break
            if found:
                break
            for web in noweb_lst:
                if set( web ) == set( permweb ):
                    found = True
                    break
            if found:
                break


        if not found:
            noweb_lst += [noweb]



    print( ' --- ' )
    for web in noweb_lst:
        print( web )



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
    # NSTools.get_tool_dct().clear()  # uncomment to remove all cache!

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

    # usecase__get_tool_dct()
    # usecase__get_cls_root_bases( rank )
    # usecase__get_cls_real_dp( rank )
    # usecase__get_classes_dp1( rank )
    usecase__get_webs( rank )
    # usecase__circles()  # does not terminate within reasonable time

    #########################################
    #                                       #
    # End of list of use case methods.      #
    #                                       #
    #########################################

    NSTools.end_timer()
    print( '\nThe End' )



