'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 9, 2017
@author: Niels Lubbes
'''

import time

from sage_interface import sage_identity_matrix
from sage_interface import sage_matrix
from sage_interface import sage_ZZ
from sage_interface import sage_Permutations
from sage_interface import sage_Subsets
from sage_interface import sage_n

from class_div import Div

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


def contains_perm( f_lst_lst, c_lst ):
    '''
    Parameters
    ----------
    f_lst_lst : list<list<Div>>
        A list of list containing Div objects.
    
    c_lst : list<Div>
        A list of Div objects
    
    Returns:
    --------
    bool
        Returns True if after a permutation of the generators
        (e1,...,er) the list c_lst is contained in f_lst_lst. 
        For example if c_lst equals [ e0-e1, 2e0-e2-e3-e4-e5 ] 
        then is contained in [ ..., [e0-e2, 2e0-e1-e3-e4-e5], ... ].
    
    '''
    if c_lst == []:
        return [] in f_lst_lst

    for perm in sage_Permutations( range( c_lst[0].rank() - 1 ) ):
        pc_lst = [ Div( [c[0]] + [ c[i + 1] for i in perm ], c.rank() ) for c in c_lst ]
        for f_lst in f_lst_lst:
            if set( f_lst ) == set( pc_lst ):
                return True

    return False


def nonreducible_intersect_webs( dpl, numline, numfam, int_lst ):
    '''
    Parameters
    ----------
    dpl : DPLattice
    
    numline : int
    
    numfam : int
    
    int_lst : list<int>
        List of intersection numbers. Should not contain 0.
    
    Returns
    -------
    list<list<Div>>
        All lists of real families in "dpl" of length "numfam", so that 
        there does not exists "numline" pairwise orthogonal real lines 
        that are orthogonal to the families as well. Moreover we require
        the number of intersections between two families is in "int_lst".
        If "int_lst==[]", then no restrictions are imposed.
    '''
    key = 'nonreducible_intersect_webs__' + str( ( dpl.real_fam_lst, dpl.real_m1_lst, numline, numfam, int_lst ) )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    f_lst_lst = []

    if numfam == 1:
        if len( dpl.real_m1_lst ) < numline:
            f_lst_lst = [ [f] for f in dpl.real_fam_lst ]
    else:
        # data for ETA computation
        ostart = time.time()
        counter = 0
        total = len( dpl.real_fam_lst )
        ival = 10

        for f in dpl.real_fam_lst:

            # ETA
            if counter % ival == 0:
                istart = time.time()
            counter += 1
            if counter % ival == 0:
                itime = ( time.time() - istart ) / ( 60 * ival )
                otime = ( time.time() - ostart ) / 60
                spc = '' + max( ( 3 - numfam ), 0 ) * '\t'
                NSTools.p( spc,
                           'ETA =', sage_n( itime * ( total - counter ), digits = 5 ),
                           'm, counter =', counter, '/', total,
                           ', time =', sage_n( otime, digits = 5 ),
                           'm, rank =', dpl.get_rank() )

            fdpl = DPLattice( dpl.d_lst, dpl.Md_lst, dpl.M )
            if int_lst != []:
                fdpl.real_fam_lst = [ f2 for f2 in dpl.real_fam_lst if f2 * f in int_lst ]
            else:
                fdpl.real_fam_lst = [ f2 for f2 in dpl.real_fam_lst if f2 * f != 0 ]
            fdpl.real_m1_lst = [ m for m in dpl.real_m1_lst if m * f == 0 ]
            rf_lst_lst = nonreducible_intersect_webs( fdpl, numline, numfam - 1, int_lst )
            for f_lst in rf_lst_lst:
                f_lst_lst += [[f] + f_lst]

    if numfam > 2:
        # cache output
        NSTools.get_tool_dct()[key] = f_lst_lst
        NSTools.save_tool_dct()

    return f_lst_lst



def nonreducible_webs( dpl, numline, numfam = 3 ):
    '''
    Parameters
    ----------
    dpl : DPLattice
    numline : int
    numfam : int
    
    Returns
    -------
    list<list<Div>>
        All lists of real families in "dpl" of length "numfam", so that 
        there does not exists "numline" pairwise orthogonal real lines 
        that are orthogonal to the families as well. 
    '''
    key = 'nonreducible_webs__' + str( dpl ).replace( '\n', '---' ) + '__' + str( ( numline, numfam ) )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    idx_f_lst = sage_Subsets( range( len( dpl.real_fam_lst ) ), numfam )

    # data for ETA computation
    ostart = time.time()
    counter = 0
    total = len( idx_f_lst )
    ival = 10

    NSTools.p( dpl )

    f_lst_lst = []
    for idx_f in idx_f_lst:

        # ETA
        if counter % ival == 0:
            istart = time.time()
        counter += 1
        if counter % ival == 0:
            itime = ( time.time() - istart ) / ( 60 * ival )
            otime = ( time.time() - ostart ) / 60
            NSTools.p( 'ETA =', sage_n( itime * ( total - counter ), digits = 5 ),
                       'm, counter =', counter, '/', total,
                       ', time =', sage_n( otime, digits = 5 ),
                       'm, rank =', dpl.get_rank() )


        reduce = False

        f_lst = [ dpl.real_fam_lst[idx] for idx in idx_f ]

        om_lst = []
        for om in dpl.real_m1_lst:
            if set( [om * f for f in f_lst ] ) == {0}:
                om_lst += [om]

        for idx_m in sage_Subsets( range( len( om_lst ) ), numline ):
            m_lst = [ om_lst[idx] for idx in idx_m ]

            if numline > 1 and set( [m1 * m2 for m1 in m_lst for m2 in m_lst ] ) != {0, -1}:
                continue

            reduce = True
            break

        if not reduce and not contains_perm( f_lst_lst, f_lst ):
            NSTools.p( 'nonreducible f_lst =', f_lst )
            f_lst_lst += [ f_lst ]

    # cache output
    NSTools.get_tool_dct()[key] = f_lst_lst
    NSTools.save_tool_dct()

    return f_lst_lst






