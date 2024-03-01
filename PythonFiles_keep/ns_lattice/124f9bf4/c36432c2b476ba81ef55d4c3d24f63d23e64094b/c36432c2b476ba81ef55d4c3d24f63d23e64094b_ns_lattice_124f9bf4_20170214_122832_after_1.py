'''
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
    for d_lst in get_root_bases( bnd_max_rank ):
        nt.p( get_dynkin_type( d_lst ), '\t\t\t', d_lst )


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
    d_lst = [12, 34]  # root basis
    rank = 6  # rank of NS-lattice
    Mtype = '2A1'  # root system corresponding to involution is of type D4

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
            if len( dpl.real_fam_lst ) >= 2 and len( dpl.real_m1_lst ) == 0:
                # no real lines and two families of conics

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
        print row_format.format( *row )

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

    print DPLattice.get_tex_table( celestial_dct )


if __name__ == '__main__':

    #  Debug output settings
    #
    # nt.filter( '__main__.py' ) # only print if output by module <file_name>
    nt.filter( None )
    nt.start_timer()

    #
    # Should be between 3 and 9.
    # computes classifications up to rank "max_rank".
    # If max_rank==9 then the computations take about 4 hours.
    #
    max_rank = 6

    #########################################
    #                                       #
    # Uncomment one or more use cases       #
    #                                       #
    #########################################

    usecase__get_cls_root_bases( max_rank )
    usecase__get_tool_dct()
    usecase__get_root_bases( max_rank )
    usecase__get_cls_root_bases( max_rank )
    usecase__get_cls_involutions( max_rank )
    usecase__get_involutions()
    usecase__get_cls_real_dp( max_rank )
    usecase__get_cls_real_dp__celestials( max_rank )
    usecase__get_cls_real_dp__tex( max_rank )

    #########################################
    #                                       #
    # End of list of use case methods.      #
    #                                       #
    #########################################

    # end timing
    nt.end_timer()

    print
    print 'The End'



