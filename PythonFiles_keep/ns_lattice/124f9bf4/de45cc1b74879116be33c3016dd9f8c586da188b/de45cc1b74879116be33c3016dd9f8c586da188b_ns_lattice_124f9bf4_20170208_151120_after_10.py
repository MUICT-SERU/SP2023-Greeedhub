'''
Created on Aug 11, 2016
@author: Niels Lubbes
'''

from sage.all import *

from ns_tools import *
from class_div import *
from class_dp_lattice import *
from div_set import *
from dp_involutions import *
from dp_root_bases import *


def test_div_0():
    '''
    Test the "Div.new()" and "Div.get_label()" methods.
    '''

    lbl_lst = []
    lbl_lst += ['3h+e1+5e5-e6']
    lbl_lst += [ 'e1-e2']
    lbl_lst += ['-e1+e2']
    lbl_lst += ['-3h']
    lbl_lst += ['-e3']
    lbl_lst += ['12']
    lbl_lst += ['-12']
    lbl_lst += ['1245']
    lbl_lst += ['214']
    lbl_lst += ['306']
    lbl_lst += ['-308']

    div_lst = []
    for lbl in lbl_lst:
        div_lst += [Div.new( lbl )]
        np( lbl + ' =', div_lst[-1].e_lst )

    for div in div_lst:
        np( div.e_lst, '=', div.get_label() )

    np( 10 * '-' )
    np( '1124 < 1123: ', Div.new( '1124' ) < Div.new( '1123' ) )
    np( '12   < 1123: ', Div.new( '12' ) < Div.new( '1123' ) )
    np( '13   < 12  : ', Div.new( '13' ) < Div.new( '12' ) )
    np( '34   < 12  : ', Div.new( '34' ) < Div.new( '12' ) )


def test_div_set_0():
    '''
    Test the methods in the "div_set" module.
    '''

    np( 20 * '-' )
    d = Div( [3] + 4 * [-1] )
    for div in get_div_set( d, 1, -1, True ):
        np( div )

    np( 20 * '-' )
    for div in get_m1_classes( 5, True, [] ):
        np( div )

    np( 20 * '-' )
    d = Div( [3] + 8 * [-1] )
    for div in get_div_set( d, 1, -1, False ):
        np( div )

    np( 20 * '-' )
    for div in get_m1_classes( 9, False, [] ):
        np( div )

    np( 20 * '-' )
    for div in get_m1_classes( 3, True, [] ):
        np( div )

    np( 20 * '-' )
    m2_lst = get_m2_classes( 5, True )
    m2_lst.sort( reverse = True )
    for div in m2_lst:
        np( div )

    np( 20 * '-' )
    for div in get_fam_classes( 6, False, [] ):
        np( div )

    np( 20 * '-' )
    for div in get_fam_classes( 6, True, [] ):
        np( div )


    np( 20 * '-' )
    for div in get_m1_classes( 4, True, [] ):
        np( div )

    np( 20 * '-' )




def test_dp_root_bases_0( max_rank ):
    '''
    Test "dp_root_bases.get_cls_root_bases(max_rank)".
    '''

    for rank in range( 3, max_rank + 1 ):
        d_lst_lst = get_cls_root_bases( max_rank )[rank]
        np( 10 * '-' )
        i = 1
        for d_lst in d_lst_lst:
            np( i, '<' + str( rank ) + '>', ': ', get_dynkin_type( d_lst ), '\t\t', d_lst )
            i += 1
        np( '# =', len( d_lst_lst ) )


def test_dp_root_bases_1():
    '''
    Test "dp_root_bases.get_dynkin_type()".
    '''

    for ( G, ts, t_lst ) in get_tool_dct()["get_dynkin_type"]:
        np( ts, t_lst, G )


def test_dp_root_bases_2():
    '''
    Test "dp_root_bases.get_root_bases()" for rank 6 (degree 4 Del Pezzo).
    '''

    for d_lst in get_root_bases( 6 ):
        np( get_dynkin_type( d_lst ), '\t\t\t', d_lst )


def test_dp_involutions_0():
    '''
    Test "dp_involutions.complete_basis()".
    '''

    d_lst = [ 34, 45]
    rank = 6
    d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
    mat = complete_basis( d_lst )
    np( rank, d_lst )
    np( '\n' + str( mat ) )
    np( 10 * '-' )


    d_lst = [ 23, 34, 45 ]
    rank = 6
    d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
    mat = complete_basis( d_lst )
    np( rank, d_lst )
    np( '\n' + str( mat ) )
    np( 10 * '-' )

    # 4A1
    d_lst = [ 1123, 12, 23, 45 ]
    rank = 6
    d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
    mat = complete_basis( d_lst )
    np( rank, d_lst )
    np( '\n' + str( mat ) )
    np( 10 * '-' )


    d_lst = [ 1145, 23 ]
    rank = 6
    d_lst = [ Div.new( str( d ), rank ) for d in d_lst ]
    mat = complete_basis( d_lst )
    np( rank, d_lst )
    np( '\n' + str( mat ) )
    np( 10 * '-' )


def test_dp_involutions_1( max_rank ):
    '''
    Test "dp_involutions.get_cls_involutions(max_rank)".
    '''

    invo_cls_dct = get_cls_involutions( max_rank )
    for rank in range( 3, max_rank + 1 ):
        np( 10 * '-' )
        for ( M, d_lst ) in invo_cls_dct[rank]:
            np( rank, get_dynkin_type( d_lst ), d_lst, list( M ) )

            b_lst = [Div( row ) for row in identity_matrix( ZZ, rank ).rows() ]
            np( '\t', [b.mat_mul( M ).get_label( True ) for b in b_lst] )


def test_dp_involutions_2():
    '''
    List all compatible involutions for a fixed root basis.
    '''
    d_lst = []
    rank = 6
    Mtype = 'D4'
    for ( M, Md_lst ) in get_involutions( rank ):

        # check whether involution M preserves d_lst
        dm_lst = [ d.mat_mul( M ) for d in d_lst ]
        if sorted( dm_lst ) != sorted( d_lst ):
            continue

        dpl = DPLattice.init( d_lst, Md_lst, M )
        if dpl.Mtype != Mtype:
            continue

        np( dpl )

        k = Div( [-3] + ( rank - 1 ) * [1] )
        if k.mat_mul( M ) != k:
            raise Exception( 'The canonical class should be preserved M(k)=', k.mat_mul( M ) )


        # np( rank, get_dynkin_type( d_lst ), d_lst, list( M ) )
        # b_lst = [Div( row ) for row in identity_matrix( ZZ, rank ).rows() ]
        # np( '\t', [b.mat_mul( M ).get_label( True ) for b in b_lst] )




def test_dp_lattice_0( max_rank ):
    '''
    Test "DPLattice.get_cls_real_dp(...)".
    '''
    np( 'max_rank =', max_rank )

    # provable version of the classification algorithm.
    #
    dp_cls_dct_1 = DPLattice.get_cls_real_dp( min( max_rank, 7 ), True )
    for rank in range( 3, max_rank + 1 ):
        for dpl in dp_cls_dct_1[rank]:
            np( dpl )

    np( 5 * ( 10 * '#' + '\n' ) )

    # non provable version of classification where the
    # number of involutions is minimized
    #
    dp_cls_dct_2 = DPLattice.get_cls_real_dp( min( max_rank, 7 ), False )
    for rank in range( 3, max_rank + 1 ):
        for dpl in dp_cls_dct_2[rank]:
            if dpl in dp_cls_dct_1[rank] and len( dp_cls_dct_1[rank] ) == len( dp_cls_dct_2[rank] ):
                np( dpl )
            else:
                err_str = '''
                The provable and non-provable version of the 
                classification algorithm 
                    "DPLattice.get_cls_real_dp()" 
                do not agree.
                '''
                raise Exception( err_str )

    # print out a table
    #
    for rank in range( 3, max_rank + 1 ):
        for dpl in dp_cls_dct_2[rank]:
            # (#families, degree ), involution, isolated singularities
            np( ( len( dpl.real_fam_lst ), dpl.get_degree() ), dpl.Mtype, dpl.type )


def test_dp_lattice_1( max_rank ):
    '''
    Test classification of surfaces with at least 2 real families
    of circles and no real lines.  
    '''

    dp_cls_dct = DPLattice.get_cls_real_dp( min( max_rank, 7 ), False )
    celestial_dct = {}
    table = []
    for rank in range( 3, max_rank + 1 ):
        for dpl in sorted( dp_cls_dct[rank] ):
            if len( dpl.real_fam_lst ) >= 2 and len( dpl.real_m1_lst ) == 0:

                np( dpl )

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
        np( 'deg =', 10 - rank, ' #lattice-classes =', len( celestial_dct[rank] ) )


def test_dp_lattice_2( max_rank ):
    '''
    We construct a Tex string for a table with 
    a classification of celestials.
    '''
    dp_cls_dct = DPLattice.get_cls_real_dp( min( max_rank, 7 ), False )
    celestial_dct = {}
    for rank in range( 3, max_rank + 1 ):
        for dpl in sorted( dp_cls_dct[rank] ):
            if len( dpl.real_fam_lst ) >= 2 and len( dpl.real_m1_lst ) == 0:
                if rank not in celestial_dct:
                    celestial_dct[rank] = []
                celestial_dct[rank] += [dpl]

    print DPLattice.get_tex_table( celestial_dct )



if __name__ == '__main__':

    #  Debug output settings
    #
    # np( True )  # show all output (this will be altered in the test methods!)
    np( False, 'ns_main.py' )  # show only when np() is called from here.
    nt( True )  # show timing

    #
    # Should be between 3 and 9.
    # computes classifications up to rank "max_rank".
    # If max_rank==9 then the computations take about 4 hours.
    max_rank = 6

    #########################################
    #                                       #
    # Uncomment one or more test methods    #
    #                                       #
    #########################################

    # test_div_0()  #                       Div object
    # test_div_set_0()  #                   div_set
    # test_dp_root_bases_0( max_rank )  #   classification singularities
    # test_dp_root_bases_1()  #             get_dynkin_type()
    # test_dp_root_bases_2()  #             get_root_basis(rank)
    # test_dp_involutions_0()  #            complete_basis(d_lst)
    # test_dp_involutions_1( max_rank )  #  classification involutions
    test_dp_involutions_2()  #             list all compatible involutions for a fixed root basis
    # test_dp_lattice_0( max_rank )  #      classification lattices
    # test_dp_lattice_1( max_rank )  #      classification celestials
    # test_dp_lattice_2( max_rank )  #      construct Tex string for table for classification celestials

    #########################################
    #                                       #
    # End of list of test methods.          #
    #                                       #
    #########################################

    # end timing
    nt()

    print
    print 'The End'



