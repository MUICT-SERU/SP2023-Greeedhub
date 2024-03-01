'''
Created on Aug 11, 2016
@author: Niels

See [http://arxiv.org/abs/1302.6678] for more info.

Classification of root subsystems of root systems
of type either A1, A1+A2, A4, D5, E6, E7 or E8.
'''
from sage_interface import sage_VectorSpace
from sage_interface import sage_QQ
from sage_interface import sage_identity_matrix
from sage_interface import sage_Graph
from sage_interface import sage_Partitions
from sage_interface import sage_RootSystem
from sage_interface import sage_Subsets
from sage_interface import sage_Combinations
from sage_interface import sage_Permutations


from class_ns_tools import NSTools
from class_div import Div

from div_in_lattice import get_divs
from div_in_lattice import get_indecomp_divs
from div_in_lattice import get_ak


def is_root_basis( d_lst ):
    '''
    Parameters
    ----------
    d_lst : list<Div> 
        A list of lists of "Div" objects "d", 
        such that d*d=-2 and d*(-3h+e1+...+er)=0 
        where r=rank-1 and rank in [3,...,7].
               
    Returns
    -------
    bool
        True if input is the empty list or if divisors 
        in "d_lst" are linear independent as vectors
        and their pairwise product is either -2, 0 or 1.        
    '''

    if d_lst == []:
        return True

    # check pairwise inner product
    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] not in [0, 1, -2]:
                return False

    # check linear independence
    V = sage_VectorSpace( sage_QQ, d_lst[0].rank() )
    W = V.subspace( [d.e_lst for d in d_lst] )
    return W.rank() == len( d_lst )


def get_graph( d_lst ):
    '''
    Parameters
    ----------
    d_lst : list<Div>
        A list of "Div" objects.

    Returns
    -------
    sage_Graph

        A labeled "Graph()" where the elements
        of "d_lst" are the vertices.
        Different vertices are connected if
        their corresponding intersection product
        is non-zero and the edge is labeled with
        the intersection product.
    '''
    G = sage_Graph()
    G.add_vertices( range( len( d_lst ) ) );

    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] > 0 and i != j:
                G.add_edge( i, j, d_lst[i] * d_lst[j] )

    return G


def get_ext_graph( d_lst, M ):
    '''
    Parameters
    ----------
    d_lst : list<Div> 
        A list of "Div" objects of equal rank.
        
    M : sage_matrix<sage_ZZ>   
        A square matrix with integral coefficients
        of rank "d_lst[0].rank()" 
    
    Returns
    -------
        A labeled "sage_Graph()" where the elements 
        of "d_lst" are the vertices. 
        A pair of vertices are connected 
        by and edge labeled with their 
        non-zero intersection product. 
        Two vertices which are related 
        via M are connected with an edge labeled 1000.
        Labeled self-loops are also included.
        Two orthogonal vertices are connected 
    '''
    G = sage_Graph()
    G.add_vertices( range( len( d_lst ) ) )

    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] != 0:
                G.add_edge( i, j, d_lst[i] * d_lst[j] )

    for i in range( len( d_lst ) ):
        j = d_lst.index( d_lst[i].mat_mul( M ) )
        G.add_edge( i, j, 1000 )

    return G


def is_equal_root_bases( d_lst1, d_lst2 ):
    '''Test equality of root bases
    
    Check whether "d_lst1" and "d_lst2"
    are bases of isomorphic root subsystems by using
    the Cremona invariant. This is a graph
    whose vertices are Div object "d" such that
        ( d*k, d*d ) in [ (-1,-1), (0,-2)]
    where k=3e0-e1-...-er. 


    Parameters
    ----------
    d_lst1 : list<Div>
        A list of lists of "Div" objects "d" such that 
        each "d" has the same rank.        

    d_lst2 : list<Div>
        A list of lists of "Div" objects "d" such that 
        each "d" has the same rank as any element in d_lst1.        

    Returns
    -------
    bool
        True if "d_lst1" and "d_lst2" are equivalent
        as root sub systems in the root system with
        Dynkin type either

              A1, A1+A2, A4, D5, E6, E7 or E8.
    '''

    # check cardinality
    if len( d_lst1 ) != len( d_lst2 ):
        return False

    # empty root bases are equivalent
    if len( d_lst1 ) == 0:
        return True

    # check rank
    if d_lst1[0].rank() != d_lst2[0].rank():
        return False

    rank = d_lst1[0].rank()

    M = sage_identity_matrix( sage_QQ, rank )  # real structure is the identity
    m1_lst = get_divs( get_ak( rank ), 1, -1, True )

    G1 = get_ext_graph( m1_lst + d_lst1, M )
    G2 = get_ext_graph( m1_lst + d_lst2, M )

    return G1.is_isomorphic( G2, edge_labels = True )


def get_dynkin_type( d_lst ):
    '''
    Parameters
    ----------
    d_lst : list<Div>
        A list of lists of "Div" objects "d" of 
        the same rank, such that 
            d*d=-2 and d*(-3h+e1+...+er)=0 
        where 
            r=rank-1 and rank in [3,...,9].  
        We assume that "is_root_basis(d_lst)==True":
        linear independent, self intersection number -2
        and pairwise product either 0 or 1.            
                     
    Returns
    -------
    string
        Returns a string denoting the Dynkin type of a 
        root system with basis "d_lst".  
        Returns 'A0' if "d_lst==[]".
    
    Note
    ----
        For example:
        [<1145>, <1123>, <23>, <45>, <56>, <78>] --> '3A1+A3'
        where <1145> is shorthand for "Div.new('1145')".      
        
    Raises
    ------
    ValueError
        If the Dynkin type of d_lst cannot be recognized.
         
    '''
    if d_lst == []: return 'A0'

    # check whether values are cached
    #
    construct_dynkin_types = True
    max_r = d_lst[0].rank() - 1
    key = 'get_dynkin_type_' + str( max_r )
    for r in range( max_r, 8 + 1 ):
        if 'get_dynkin_type_' + str( r ) in NSTools.get_tool_dct():
            key = 'get_dynkin_type_' + str( r )
            construct_dynkin_types = False

    # construct list of dynkin types if values are not cached
    #
    if construct_dynkin_types:
        NSTools.p( 'Constructing list of Dynkin types... max_r =', max_r )

        ade_lst = []
        for comb_lst in sage_Combinations( max_r * ['A', 'D', 'E'], max_r ):
            for perm_lst in sage_Permutations( comb_lst ):
                ade_lst += [perm_lst]
        #
        # "ade_lst" contains all combinations of 'A', 'D', 'E'
        # and looks as follows:
        #
        #     ade_lst[0] = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A']
        #     ade_lst[1] = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'D']
        #     ade_lst[2] = ['A', 'A', 'A', 'A', 'A', 'A', 'D', 'A']
        #     ...
        #     ade_lst[?] = ['A', 'D', 'A', 'D', 'A', 'D', 'E', 'A']
        #     ...
        #     ade_lst[-1]= ['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
        #

        type_lst = []
        ts_lst = []
        for ade in ade_lst:
            for r in range( 1, max_r + 1 ):
                for p_lst in sage_Partitions( r + max_r, length = max_r ):

                    # obtain type list
                    t_lst = [( ade[i], p_lst[i] - 1 ) for i in range( max_r ) if  p_lst[i] != 1]
                    t_lst.sort()

                    # obtain Root system
                    # or continue if invalid Cartan/Dynkin type
                    if ( 'D', 2 ) in t_lst or ( 'D', 3 ) in t_lst:
                        continue
                    try:
                        rs = sage_RootSystem( t_lst )
                    except ValueError as err:
                        continue  # not a valid Cartan type

                    # obtain graph G
                    mat = list( -1 * rs.cartan_matrix() )
                    G = sage_Graph()
                    G.add_vertices( range( len( mat ) ) );
                    for i in range( len( mat ) ):
                        for j in range( len( mat[0] ) ):
                           if mat[i][j] == 1:
                               G.add_edge( i, j )

                    # obtain string for type
                    # Example: [(A,1),(A,1),(A,1),(A,3)] ---> '3A1+A3'
                    tmp_lst = [t for t in t_lst]
                    ts = ''
                    while len( tmp_lst ) > 0:
                        t = tmp_lst[0]
                        c = tmp_lst.count( t )
                        while t in tmp_lst:
                            tmp_lst.remove( t )
                        if ts != '':
                            ts += '+'
                        if c > 1:
                            ts += str( c )

                        ts += t[0] + str( t[1] )

                    # add to type_lst if new
                    if ts not in ts_lst:
                        type_lst += [( G, ts, t_lst )]
                        ts_lst += [ts]
                        NSTools.p( 'added to list: ', ts, '\t\t...please wait...' )

        NSTools.p( 'Finished constructing list of Dynkin types.' )
        # cache the constructed "type_lst"
        NSTools.get_tool_dct()[key] = type_lst
        NSTools.save_tool_dct()

    # end if
    else:
        type_lst = NSTools.get_tool_dct()[key]
    G1 = get_graph( d_lst )

    # loop through all types and check equivalence
    for ( G2, ts, t_lst ) in type_lst:
        if G1.is_isomorphic( G2 ):
            return ts

    raise ValueError( 'Could not recognize Dynkin type: ', d_lst )


def get_root_bases_orbit( d_lst, positive = False ):
    '''Returns the orbit of a root base under the Weyl group.
    
    Parameters
    ----------
    d_lst : list<Div>
        A list of lists of "Div" objects "d" of the same rank or the empty list.    

    positive : bool
    
    Returns
    -------
    list<list<Div>>
        A list of distinct lists of "Div" objects "d" of the same rank. 
        such that d*d=-2 and d*(-3h+e1+...+er)=0 where r=rank-1.
        
        If "d_lst" is the empty list, then "[]" is returned.
        
        Otherwise we return a list of root bases such that each root basis
        is obtained as follows from a root "s" such that s*s=-2 
        and s*(-3h+e1+...+er)=0: 
        
            [ d + (d*s)d for d in d_lst ]
        
        We do this for all possible roots in [s1,s2,s3,...]: 
        
            [ [ d + (d*s1)d for d in d_lst ],  [ d + (d*s2)d for d in d_lst ], ... ]
         
        Mathematically, this means that we consider the Weyl group 
        of the root system with Dynkin type determined by the rank of elements 
        in "d_lst". The Dynkin type is either 
            A1, A1+A2, A4, D5, E6, E7 or E8.
        We return the orbit of the elements in "d_lst" under
        the action of the Weyl group.
                
        If "positive==True" then the roots in the basis are all positive
        and thus of the form 
            <ij>, <1ijk>, <2ij>, <30i>
        with i<j<k. 
        For example '15' and '1124' but not '-15' or '-1124'. 
        See "Div.get_label()" for the notation.                           
    '''
    key = 'get_root_bases_orbit' + str( d_lst )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    if d_lst == []:
        return []

    # obtain list of all (-2)-classes
    m2_lst = get_divs( get_ak( d_lst[0].rank() ), 0, -2, True )
    m2_lst += [ m2.int_mul( -1 ) for m2 in m2_lst]
    NSTools.p( 'd_lst  =', d_lst )
    NSTools.p( 'm2_lst =', len( m2_lst ), m2_lst )

    d_lst_lst = [d_lst]
    for cd_lst in d_lst_lst:
        for m2 in m2_lst:

            #
            # The action of roots on a root base is by reflection:
            #     cd - 2(cd*m2/m2*m2)m2
            # Notice that m2*m2==-2.
            #
            od_lst = [ cd + m2.int_mul( cd * m2 ) for cd in cd_lst]
            print( 'm2 =', m2, ', od_lst =', od_lst, ', cd_lst =', cd_lst, ', d_lst_lst =', d_lst_lst, ' positive =', positive )

            if not is_root_basis( od_lst ):
                raise Exception( 'Unexpected position: the Weyl group should ' +
                                 'act transitively on root bases!\n' +
                                 'cd_lst =', cd_lst, ', m2 =', m2, ' od_lst =', od_lst )

            if positive and '-' in [ od.get_label( True )[0] for od in od_lst ]:
                continue  # continue with for loop since a negative root in basis

            if od_lst not in d_lst_lst:
                d_lst_lst += [od_lst]


    # cache output
    NSTools.get_tool_dct()[key] = d_lst_lst
    NSTools.save_tool_dct()

    NSTools.p( 'orbit(' + str( d_lst ) + ') =', d_lst_lst )

    return d_lst_lst


def get_root_bases( rank, positive = False, fast = True ):
    '''Returns all root bases of given rank.
    
    Parameters
    ---------- 
    rank : int
        An integer between 3 and 9.
    
    positive : bool
    
    fast: bool
        If False then the root bases are computed by
        exhaustive search.
    
    Returns
    -------
    list<Div>
        Returns a list of lists of "Div" objects "d", 
        such that d*d=-2 and d*(-3h+e1+...+er)=0 where r=rank-1.
        The empty list is included.
         
        The list of "Div" objects represent a list of (-2)-classes
        that form a basis for a root subsystem of the root system
        with Dynkin type either:
            A1, A1+A2, A4, D5, E6, E7 or E8,
        corresponding to ranks 3, 4, 5, 6, 7, 8 and 9 respectively
        (eg. A1+A2 if rank equals 4, and E8 if rank equals 9).
        Note that the root systems live in the vector space 
        associated to the Neron-Severi lattice of a weak Del Pezzo surface.          
          
        If "positive==True" then the 
        roots in the basis are all positive
        and thus of the form <ij>, <1ijk>, <2ij>, <30i>
        with i<j<k. For example '15' and '1124' 
        but not '-15' or '-1124' 
        (see "Div.get_label()" for notation).  
          
        The output list is sorted with respect to the string of the Dynkin type.
        Each root basis in the list is sorted as a list of Div objects.         
    '''
    # already computed before?
    key = 'get_root_bases_' + str( rank ) + '_' + str( positive ) + '_' + str( fast )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    NSTools.p( 'Constructing root bases for rank', rank, '...' )
    d_lst_lst = [[]]

    if fast:

        # for each root basis representative we obtain its
        # orbit and thus we obtain all root bases.
        #
        for d_lst in get_cls_root_bases( rank )[rank]:
            NSTools.p( 'computing orbit of ', get_dynkin_type( d_lst ), ' d_lst =', d_lst )
            d_lst_lst += get_root_bases_orbit( d_lst, positive )

    else:
        # perform exhaustive search

        # construct list of (-2)-classes
        m2_lst = get_divs( get_ak( rank ), 0, -2, True )
        if not positive:
            m2_lst += [ m2.int_mul( -1 ) for m2 in m2_lst]

        # loop through all subsets of list of (-2)-classes of length at most rank-1.
        for r in range( 1, rank ):

            # go through all possible root bases of length r
            NSTools.p( r, '/', rank - 1, ', length list =', len( m2_lst ), ', rank =', rank )
            for idx_lst in sage_Subsets( range( len( m2_lst ) ), r ):

                # construct sub-list
                d_lst1 = [ m2_lst[idx] for idx in idx_lst ]

                # add if root basis
                if is_root_basis( d_lst1 ):
                    d_lst1.sort()
                    d_lst_lst += [d_lst1]


    # sort list
    d_lst_lst.sort( key = lambda d_lst: get_dynkin_type( d_lst ) )

    # cache output
    NSTools.get_tool_dct()[key] = d_lst_lst
    NSTools.save_tool_dct()

    return d_lst_lst


def get_cls_root_bases( max_rank = 9 ):
    '''
    See [Algorithm 5, http://arxiv.org/abs/1302.6678] for more info. 
    
    Parameters
    ----------
    max_rank : int
        An integer in [3,...,9].
    
    Returns
    -------
    dict
        A dictionary "bases_cls_dct" such that 
        "bases_cls_dct[rank]" is a list of lists of "Div" objects "d", 
        such that d*d=-2 and d*(-3h+e1+...+er)=0 where r=rank-1.
        The empty list is included.
        We classify for rank in [3,...,max_rank].
         
        The list of "Div" objects represent a list of (-2)-classes
        that form a basis for a root subsystem of the root system
        with Dynkin type either:
            A1, A1+A2, A4, D5, E6, E7 or E8,
        corresponding to ranks 3, 4, 5, 6, 7, 8 and 9 respectively 
        (eg. A1+A2 if rank equals 4, and E8 if rank equals 9).
        Note that the root systems live in a subspace of the vector space 
        associated to the Neron-Severi lattice of a weak Del Pezzo surface.
    
        The list "bases_cls_dct[rank]" contains exactly one 
        representative for all root subsystems up to equivalence.         
    '''
    # classification of root bases in cache?
    for rank in range( max_rank, 9 + 1 ):
        key = 'get_cls_root_bases_' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]
    key = 'get_cls_root_bases_' + str( max_rank )


    A = [ 12, 23, 34, 45, 56, 67, 78]

    #################
    # maximal bases #
    #################

    #
    # A{k}+A{n-k-1}, A{k}
    # E7: A1+D6
    # E8: E8
    #
    Z1 = A + [1123, 1145]

    #
    # E6: E6, D5, A1+A5, 3A2
    # E7: E7, A2+A5
    # E8: E7+A1,  A2+E6,
    #
    Z2 = A + [1123, 1456]

    # E7: A7
    Z3 = A[:-1] + [278]

    # E8: A8
    Z4 = A + [1123, 1567]

    # E8: 2A4
    Z5 = A + [278, 1678]

    Z_lst = [Z1, Z2, Z3, Z4, Z5]

    #################
    # END           #
    #################


    # A = [ 12, 23, 34, 45, 56, 67, 78]
    # Z1 = A + [ 1123 ]
    # Z2 = A + [ 1123, 1145, 1678, 234 ]
    # Z3 = A + [ 278, 1567, 1347, 1127 ]  # D4+4A1
    # Z4 = A + [ 1123, 1456, 1678, 1347 ]  # 2A3+A1
    # Z5 = A + [ 1567, 1347, 1127, 1145 ]  # A7, D4+3A1, D4+A3
    # Z6 = [ 12, 34, 56, 308, 278, 1567, 1347, 1127 ]  # 8A1
    # Z_lst = []
    # Z1 = [ 12, 23, 34, 45, 56, 67, 78, 1123 ]
    # Z2 = [ 12, 23, 34, 45, 56, 67, 78, 1123, 1145, 1347, 1678, 1127, 1456, 1567, 234, 278, 308 ]
    # Z3 = [ 1123, 1345, 1165, 1285, 1673, 1274, 1684, 1178 ]
    # Z0 = [ 12, 23, 34, 45, 56, 67, 78, 1123, -1145, -1345, -1167, -1178, -278, -218, -308, 218 ]
    # Z_lst = [Z1, Z2, Z3, Z0]
    # Z_lst = []
    # Z_lst += [[12, 23, 34, 45, 56, 67, 78]]
    # Z_lst += [ Z_lst[0] + [1123, 1127, 1145, 1347, 1567]]
    # Z_lst += [ Z_lst[0] + [1127, 1347, 1567, 278, 308 ]]
    # Z_lst += [ Z_lst[0] + [1123, 1145, 1347, 1456, 1678 ]]
    # Z_lst += [[ 1123, 1345, 1165, 1285, 1673, 1274, 1684, 1178 ]]


    bases_cls_dct = {}
    for rank in range( 3, max_rank + 1 ):

        d_lst_lst = [[]]  # include empty list
        for Z in Z_lst:

            # consider all subsets of Z of length at most rank-1
            NSTools.p( 'rank =', rank )
            NSTools.p( 'Z before =', Z )
            Z = [ Div.new( str( z ), rank ) for z in Z if rank >= Div.get_min_rank( str( z ) )]
            NSTools.p( 'Z after  =', Z )
            for i in range( 1, rank ):

                NSTools.p( '\trank subsystem =', i, '\trank =', rank, )
                for idx_lst in sage_Subsets( range( len( Z ) ), i ):

                    # recover subset of Z from indices
                    d_lst1 = [ Z[idx] for idx in idx_lst ]

                    # check whether d_lst1 is a root basis
                    if not is_root_basis( d_lst1 ):
                        continue

                    # check whether d_lst1 is new
                    new_d_lst = True
                    for d_lst2 in d_lst_lst:
                        if is_equal_root_bases( d_lst1, d_lst2 ):
                            new_d_lst = False
                            break

                    # add if new d_lst is found
                    if new_d_lst:
                        d_lst_lst += [d_lst1]

        # add list to dictionary
        bases_cls_dct[rank] = d_lst_lst

    # cache output
    NSTools.get_tool_dct()[key] = bases_cls_dct
    NSTools.save_tool_dct()

    return bases_cls_dct





#
#
# def get_orthogonal_roots( d_lst ):
#     '''
#     Parameters
#     ----------
#     d_lst : list<Div>
#         A list of "Div" objects "d" of the same rank.
#
#     Returns
#     -------
#     list<Div>
#         Returns a list of "Div" objects, which represent
#         (-2)-classes of rank "r", that are orthogonal to elements in "d_lst".
#     '''
#     m2_lst = get_divs( get_ak( d_lst[0].rank() ), 0, -2, True )
#
#     out_lst = []
#     for m2 in m2_lst:
#         if [m2 * d for d in d_lst] == len( d_lst ) * [0]:
#             out_lst += [m2]
#
#     return out_lst
#
#
# def get_subspace_roots( d_lst ):
#     '''
#     Parameters
#     ----------
#     d_lst : list<Div>
#         A list of lists of "Div" objects.
#
#     Returns
#     -------
#     list<Div>
#         Returns a list of "Div" objects, which represent
#         (-2)-classes of rank "r" that are contained in the
#         subspace spanned by "d_lst".
#     '''
#     V = sage_VectorSpace( sage_QQ, d_lst[0].rank() )
#     W = V.subspace( [d.e_lst for d in d_lst] )
#
#     m2_lst = get_divs( get_ak( d_lst[0].rank() ), 0, -2, True )
#
#     out_lst = []
#     for m2 in m2_lst:
#         if sage_vector( m2.e_lst ) in W:
#             out_lst += [ m2 ]
#
#     return out_lst
#
#
# def is_equal_root_lst( d_lst1, d_lst2 ):
#     '''
#     Check whether "d_lst1" and "d_lst2"
#     are bases of isomorphic root subsystems by using
#     "get_orthogonal_roots()" and "get_subspace_roots()".
#     These methods return invariants for root subsystems.
#
#     See [Proposition 3, http://arxiv.org/abs/1302.6678] for more info.
#
#     Parameters
#     ----------
#     d_lst1 : list<Div>
#         A list of lists of "Div" objects "d".
#
#     d_lst2 : list<Div>
#         A list of lists of "Div" objects "d".
#
#     Returns
#     -------
#     bool
#         True if "d_lst1" and "d_lst2" are equivalent
#         as root sub systems in the root system with
#         Dynkin type either
#
#               A1, A1+A2, A4, D5, E6, E7 or E8.
#
#         These root systems live in a subspace of an
#         inner-product space with signature (1,rank-1).
#         The subspace is the (rank-1)-space orthogonal to
#         -3h+e1+...+er.
#     '''
#     # ``rss'' is short hand for ``root subsystem''
#
#     # check cardinality
#     if len( d_lst1 ) != len( d_lst2 ):
#         return False
#
#     # empty root bases are equivalent
#     if len( d_lst1 ) == 0:
#         return True
#
#     # check rank
#     if d_lst1[0].rank() != d_lst2[0].rank():
#         return False
#
#     # check number of indecomposable classes of conics
#     c_lst1 = get_divs( get_ak( d_lst1[0].rank() ), 2, 0, True )
#     c_lst2 = get_divs( get_ak( d_lst2[0].rank() ), 2, 0, True )
#     nfam1 = len( get_indecomp_divs( c_lst1, d_lst1 ) )
#     nfam2 = len( get_indecomp_divs( c_lst2, d_lst2 ) )
#     if nfam1 != nfam2:
#         return False
#
#     # check whether Graphs of rss are isomorphic
#     G1 = get_graph( d_lst1 )
#     G2 = get_graph( d_lst2 )
#     if not G1.is_isomorphic( G2 ):
#         return False
#
#     # check whether the cardinality of the
#     # roots orthoginal to d_lst# agree
#     o_lst1 = get_orthogonal_roots( d_lst1 )
#     o_lst2 = get_orthogonal_roots( d_lst2 )
#     if len( o_lst1 ) != len( o_lst2 ):
#         return False
#
#     # check whether the cardinality of the
#     # roots in subspace spanned by d_lst# agree
#     s_lst1 = get_subspace_roots( d_lst1 )
#     s_lst2 = get_subspace_roots( d_lst2 )
#     if len( s_lst1 ) != len( s_lst2 ):
#         return False
#
#     return True







