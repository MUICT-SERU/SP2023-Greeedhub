'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 9, 2017
@author: Niels Lubbes
'''

from sage_interface import sage_identity_matrix
from sage_interface import sage_matrix
from sage_interface import sage_ZZ

from div_in_lattice import get_indecomp_divs
from div_in_lattice import get_ak
from div_in_lattice import get_divs

from class_ns_tools import NSTools

from class_dp_lattice import DPLattice


def get_bases_lst( a_lst, M, d_lst, m1_lst, perm = False ):
    '''
    Returns a list of basis with specified generators.
    
    Parameters
    ----------
    a_lst : list<Div>
        A list of linear independent Div objects of 
        the same rank with 3<=rank<=9.
        It is required that
        "set(a_lst)==set([ a.mat_mul(M) for a in a_lst ])".
    
    M : sage_matrix<sage_ZZ>
        A unimodular matrix representing an involution.
    
    d_lst : list<Div>
        A list of Div objects d of the same rank as any
        element in "a_lst", so that "d*k==0" and "d*d==-2".
        These represent a root basis for the indecomposable 
        (-2)-classes in the Neron-Severi lattice of a 
        weak del Pezzo surface.   

    m1_lst : list<Div>
        A list of Div objects d of the same rank as any
        element in "a_lst", so that "d*k==d*d==-1".
        These represent (-1)-classes in the Neron-Severi 
        lattice of a weak del Pezzo surface.     
    
    perm : bool
        If False, then we consider two bases the same if the 
        generators of the first basis can be obtained from 
        the second basis via a permutation matrix.
    
    Returns
    -------
    list<tuple<Div>>
        A list of tuples of Div objects. Each tuple of Div objects
        represents a basis for the Neron-Severi lattice determined
        by d_lst and m1_lst. The bases are of the form          
            < a1,...,as, b1,...,bt >
        with the following property
            * a1,...,as are defined by the input "a_lst"
            * bi is an element in m1_lst such that bi*bj=am*bi=0 
              for all 1<=i<j<=t and 1<=m<=s              
        If "a_lst==[]" then "[[]]" is returned.   
               
    '''
    key = 'get_bases_lst__' + str( ( a_lst, M, d_lst, m1_lst, perm ) ) + '__' + str( M.rank() )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]


    if a_lst == []:
        return [[]]

    if len( a_lst ) == a_lst[0].rank():
        return [tuple( a_lst )]

    e_lst = []
    for m1 in get_indecomp_divs( m1_lst, d_lst ):
        if set( [ m1 * a for a in a_lst ] ) != {0}:
            continue
        if m1 * m1.mat_mul( M ) > 0:
            continue
        e_lst += [m1]

    bas_lst = []
    for e in e_lst:

        Me = e.mat_mul( M )
        new_d_lst = [ d for d in d_lst if d * e == d * Me == 0 ]
        new_m1_lst = [ m1 for m1 in m1_lst if m1 * e == m1 * Me == 0 ]
        add_lst = [e]
        if e != Me: add_lst += [Me]
        bas2_lst = get_bases_lst( a_lst + add_lst, M, new_d_lst, new_m1_lst, perm )

        if perm:
            bas_lst += bas2_lst
        else:
            for bas2 in bas2_lst:
                found = False
                for bas in bas_lst:
                    # check whether the two bases are the same up to
                    # permutation of generators
                    if set( bas ) == set( bas2 ):
                        found = True
                        break  # break out of nearest for loop
                if not found:
                    NSTools.p( 'found new basis: ', bas2, ', bas2_lst =', bas2_lst )
                    bas_lst += [bas2]

    # cache output
    NSTools.get_tool_dct()[key] = bas_lst
    NSTools.save_tool_dct()

    return bas_lst


def get_webs( dpl ):
    '''
    Returns lists of families of conics for each possible complex basis change.
    For example the first family in each list correspond to a fixed family wrt.
    different bases. 
    
    Parameters
    ----------
    dpl : DPLattice
        Represents the Neron-Severi lattice of a weak del Pezzo surface. 
        
    Returns
    -------
    list<list<Div>>
        A list of lists of Div objects. 
        Each Div object f has the property that 
        f*(3e0-e1-...-er)=2, f*f==0 and f*d>=0 for all d in dpl.d_lst.
        Such a Div object corresponds geometrically to a family of conics.
        For each index i, the i-th entry of each list of Div object corresponds
        to the same family of conics.          
    '''
    key = 'get_webs__' + str( dpl ).replace( '\n', '---' )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    ak = get_ak( dpl.get_rank() )
    all_m1_lst = get_divs( ak, 1, -1, True )
    akc, cc = ( 3, 1 )
    M = sage_identity_matrix( dpl.get_rank() )

    fam_lst_lst = []
    for e0 in get_divs( ak, akc, cc, True ):
        NSTools.p( 'e0 =', e0 )
        for B_lst in get_bases_lst( [e0], M, dpl.d_lst, all_m1_lst, True ):
            B = sage_matrix( sage_ZZ, [ d.e_lst for d in B_lst ] )
            dplB = dpl.get_basis_change( B )
            fam_lst_lst += [ dplB.real_fam_lst ]

    # reduce fam_lst
    pat_lst_lst = []
    rfam_lst_lst = []
    for fam_lst in fam_lst_lst:
        pat_lst = [ 0  if fam[0] != 1 else 1 for fam in fam_lst ]
        if pat_lst not in pat_lst_lst:
            pat_lst_lst += [ pat_lst ]
            rfam_lst_lst += [ fam_lst ]


    # cache output
    NSTools.get_tool_dct()[key] = rfam_lst_lst
    NSTools.save_tool_dct()

    return rfam_lst_lst



# def get_base_changes( rank, d_lst = [], div_dct = None ):
#     '''
#     Computes a basis change for a NS-lattice of a Del Pezzo surface.
#     In order to obtain such a basis, we subsequently contract
#     (-1)-curves until we arrive either at P^1xP^1 or at P^2.
#
#     INPUT:
#         - "rank"    --  An integer between 3 and 9.
#
#         - "d_lst"   --  A list of "Div" objects of the same rank==r+1
#                         such that
#                             (3e0-e1-...-er)*d==0 and d^2==-2
#                         for all d in "d_lst". Thus such divisors
#                         represent effective (-2)-classes.
#                         The intersection matrix of the Div objects
#                         is assumed to be the default: a diagonal
#                         matrix with diagonal (1,-1,...,-1).
#
#         - "div_dct" --  A dictionary representing the current NS-lattice
#                         with the following entries:
#
#                             * div_dct['ray_lst']:
#                               List of Div objects of (-1) classes that were contracted.
#                               First in list was contracted last.
#
#                             * div_dct['k']:
#                               The canonical divisor class.
#
#                             * div_dct['fam_lst']:
#                               List of Div objects f such that
#                                (3e0-e1-...-3r)*f==2 and f^2==0
#                               for all f in the list.
#                               See also "div_set.get_fam_classes()"
#
#                             * div_dct['m1_lst']:
#                               List of Div objects corresponding
#                               to (-1)-classes that can be contracted.
#                               See also "div_set.get_m1_classes()"
#
#                         For initial call the default is None.
#                         This parameter is used for recursive calls of this method.
#
#     OUTPUT:
#         - Returns a list rank*rank matrices over ZZ, such that the
#           rows of the matrix represent generators for a new basis.
#
#           There are two types of matrices in this list:
#
#             (I) The first row has self-intersection one
#                 and the remaining rows have self-intersection
#                 minus one. This basis corresponds to a basis
#                 of the Neron-Severi lattice of the projective
#                 plane P^2 blown up in points: <e0,...,er>
#                 such e0^2==1 and e1**2==-1,...er**2==-1,
#                 and the remaining intersections are zero.
#                 Thus the diagonal matrix corresponding to
#                 this bilinear intersection product has
#                 diagonal (1,-1,...,-1).
#
#            (II) The first two of the matrix have self-
#                 intersection zero and the remaining rows
#                 have self-intersection minus one.
#                 This basis corresponds to a basis of
#                 the Neron-Severi lattice of P^1xP^1
#                 blown up in points: <e0,...,er>
#                 such that e0*e1==1, e2**2==-1,...er**2==-1,
#                 and the remaining intersections are zero.
#                 Thus the matrix corresponding to this
#                 bilinear intersection product is the
#                 diagonal matrix (1, 1, -1,...,-1) with the
#                 first two columns switched.
#
#     '''
#
#     # first call?
#     first_call = ( div_dct == None )
#     if first_call:
#
#         # check if return value has been cached
#         key = 'get_base_changes' + str( rank ) + '_ ' + str( d_lst )
#         if key in nt.get_tool_dct():
#             return nt.get_tool_dct()[key]
#
#         # initialize div_dct
#         div_dct = {}
#         div_dct['ray_lst'] = []
#         div_dct['k'] = Div( [-3] + ( rank - 1 ) * [1] )  # k = -3h+e1+...+er
#         div_dct['fam_lst'] = get_fam_classes( rank, True, d_lst )
#         div_dct['m1_lst'] = get_m1_classes( rank, True, d_lst )
#
#         # check if all divisors in d_lst have equal rank
#         for d in d_lst:
#             if d.rank() != rank:
#                 raise ValueError( 'All Div objects in d_lst argument must have rank:', rank )
#
#
#     # output for debugging
#     nt.p( 10 * '-' )
#     for key in ['ray_lst', 'k', 'fam_lst', 'm1_lst']:
#         nt.p( key, '=', div_dct[key] )
#     nt.p( 'd_lst =', d_lst )
#
#
#     if div_dct['m1_lst'] == []:
#         # all rays are contracted
#
#         gen_lst = []
#
#         if len( div_dct['fam_lst'] ) == 0:
#
#             # P^2
#             ck_lst = div_dct['k'].e_lst  # k=-3e0
#             e0 = Div( [-ck / 3 for ck in ck_lst ] )
#             gen_lst = [e0] + div_dct['ray_lst']
#
#         elif len( div_dct['fam_lst'] ) == 2:
#
#             # P^1xP^1
#             gen_lst = div_dct['fam_lst'] + div_dct['ray_lst']
#
#         else:
#             # projective line bundle
#             return []
#
#         mat = matrix( ZZ, [ gen.e_lst for gen in gen_lst ] )  # rows form new basis
#         return [mat]
#
#     else:
#         # contract ray and call method recursively
#
#         mat_lst = []
#         for ray in div_dct['m1_lst']:
#
#             new_dct = {}
#             new_dct['ray_lst'] = [ray] + div_dct['ray_lst']
#             new_dct['k'] = div_dct['k'] - ray
#             new_dct['fam_lst'] = [ fam for fam in div_dct['fam_lst'] if fam * ray == 0 ]
#             new_d_lst = [ d for d in d_lst if d * ray == 0]
#
#
#             # add (-1)-curves that appeared previously as a (-2)-curve
#             new_dct['m1_lst'] = [ a for a in div_dct['m1_lst'] if a * ray == 0]
#             new_dct['m1_lst'] += [d + ray.int_mul( d * ray ) for d in d_lst if d * ray > 0]
#             for m1 in new_dct['m1_lst']:
#                 if m1 * m1 != -1 or m1 * new_dct['k'] != -1 or m1 * ray != 0:
#                     raise Exception( 'Expect only (-1)-curves orthogonal to ray.' )
#
#             mat_lst += get_base_changes( rank, new_d_lst, new_dct )
#
#         # if not recursively called by itself, cache output value
#         if first_call:
#             nt.get_tool_dct()[key] = mat_lst
#             nt.save_tool_dct()
#
#         return mat_lst
#
#
# def get_real_base_changes( dpl ):
#     '''
#     INPUT:
#         - "dp_lat"  -- DPLattice object.
#     OUTPUT
#         - "mat_lst" -- A list of matrices corresponding to base changes of
#                        the Neron-Severi lattice, which are compatible
#                        with the real structure in the following way.
#
#                        First we consider the output of ".get_base_changes()"
#                        which is a list of matrices of type (I) and (II).
#
#                        If the matrix is of type (I) with basis:
#                            <h,e1,...,er>
#                        then we include the matrix in the output list of
#                        this method, if the involution sends h to h
#                        and preserves the set {e1,..,er}.
#
#                        If the matrix is of type (II) with basis:
#                            <h,e1,...,er>
#                        then we include the matrix in the output list of
#                        this method, if the involution sends h to h,
#                        e1 to e1 and preserves the set {e2,..,er}.
#
#         - "dpl_lst" -- A list of "DPLattice" objects such that
#                        each lattice represents the same lattice
#                        as the input "dp_lat", but wrt. a different basis
#                        coming from a matrix in "mat_lst".
#     '''
#     # check if return value has been cached
#     key = 'get_real_base_changes' + str( dpl )
#     if key in nt.get_tool_dct():
#         return nt.get_tool_dct()[key]
#
#
#     mat_lst = []
#     dpl_lst = []
#     for mat in get_base_changes( dpl.get_rank(), dpl.d_lst ):
#
#         # consider list of generators and
#         # list of generators after application of involution
#         div1_lst = [ Div( row ) for row in mat ]
#         div2_lst = [ div1.mat_mul( dpl.M ) for div1 in div1_lst ]
#
#         # check whether involution preserves generators
#         for div1 in div1_lst:
#             if div1 not in div2_lst:
#                 continue
#
#         # check whether first generator is preserved
#         if div1_lst[0] != div2_lst[0]:
#             continue
#
#         # in case type (II) matrix check whether 2nd
#         # generator is preserved
#         int_lst = [ div2 * div2 for div2 in div2_lst ]
#         if int_lst[:2] == [0, 0] and div1_lst[1] != div2_lst[1]:
#             continue
#
#         # add matrix and adapted lattice
#         mat_lst += [mat]
#         dpl_lst += [ dpl.get_basis_change( mat ) ]
#
#     nt.get_tool_dct()[key] = mat_lst, dpl_lst
#     nt.save_tool_dct()
#
#     return mat_lst, dpl_lst
#
#
# if __name__ == '__main__':
#
#     # determine equivalence class
#     #
#     # rank, num_real_fam, Mtype, type = ( 6, 5, '2A1', '2A1' ) # Perseus
#     # rank, num_real_fam, Mtype, type = ( 6, 6, '2A1', 'A0' ) # Blum
#     rank, num_real_fam, Mtype, type = ( 6, 3, '2A1', '3A1' )  # CH1
#     # rank, num_real_fam, Mtype, type = ( 6, 4, '2A1', '4A1' )  # Clifford
#     # rank, num_real_fam, Mtype, type = ( 6, 3, '2A1', 'A3' )  # EY
#     # rank, num_real_fam, Mtype, type = ( 6, 2, '3A1', 'A1' )  # E and EH2
#
#
#     # find DPLattice representative for this equivalence class
#     found_dpl = None
#     for dpl in DPLattice.get_cls_real_dp( 6 )[rank]:
#         if dpl.get_numbers()[5] == num_real_fam and dpl.Mtype == Mtype and dpl.type == type:
#             found_dpl = dpl
#
#     # output
#     nt.p( found_dpl )
#     if found_dpl == None:
#         nt.p( 'exiting...' )
#         sys.exit()
#
#     # find a base change in order to construct example
#     mat_lst, dpl_lst = get_real_base_changes( found_dpl )
#     for i in range( len( mat_lst ) ):
#        mat = mat_lst[i]
#        dpl = dpl_lst[i]
#        nt.p( str( dpl ) + '\n' + str( mat.T ) + '\n\n' + str( list( mat ) ) )



