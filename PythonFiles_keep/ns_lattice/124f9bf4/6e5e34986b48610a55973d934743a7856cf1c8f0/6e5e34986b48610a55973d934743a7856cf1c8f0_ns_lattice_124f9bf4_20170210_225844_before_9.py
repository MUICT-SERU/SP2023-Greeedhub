'''
Created on Aug 11, 2016
@author: Niels

See [http://arxiv.org/abs/1302.6678] for more info.

Classification of root subsystems of root systems
of type either A1, A1+A2, A4, D5, E6, E7 or E8.
'''
from ns_lattice import *
from div_set import *

nt = NSTools()

def is_root_basis( d_lst ):
    '''
    INPUT:
        - "d_lst" -- A list of lists of "Div" objects "d", 
                     such that d*d=-2 and d*(-3h+e1+...+er)=0 
                     where r=rank-1 and rank in [3,...,7].       
    OUTPUT:
        - True if divisors in "d_lst" are linear independent as vectors
          and their pairwise product is either -2, 0 or 1.        
    '''

    # check pairwise inner product
    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] not in [0, 1, -2]:
                return False

    # check linear independence
    V = VectorSpace( QQ, d_lst[0].rank() )
    W = V.subspace( [d.e_lst for d in d_lst] )
    return W.rank() == len( d_lst )


def get_graph( d_lst ):
    '''
    INPUT:
        - "d_lst" -- A list of "Div" objects.
    OUTPUT:
        - A labeled "Graph()" where the elements 
          of "d_lst" are the vertices. 
          Different vertices are connected if 
          their corresponding intersection product
          is non-zero and the edge is labeled with 
          the intersection product. 
    '''
    G = Graph()
    G.add_vertices( range( len( d_lst ) ) );

    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] > 0 and i != j:
                G.add_edge( i, j, d_lst[i] * d_lst[j] )

    return G


def get_ext_graph( d_lst, M ):
    '''
    INPUT:
        - "d_lst" -- A list of "Div" objects of equal rank.
        - "M"     -- A square matrix with integral coefficients
                     of rank "d_lst[0].rank()" 
    OUTPUT:
        - A labeled "Graph()" where the elements 
          of "d_lst" are the vertices. 
          A pair of vertices are connected 
          by and edge labeled with their 
          non-zero intersection product. 
          Two vertices which are related 
          via M are connected with an edge labeled 1000.
          Labeled self-loops are also included.
          Two orthogonal vertices are connected 
    '''
    G = Graph()
    G.add_vertices( range( len( d_lst ) ) );

    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] != 0:
                G.add_edge( i, j, d_lst[i] * d_lst[j] )

    for i in range( len( d_lst ) ):
        j = d_lst.index( d_lst[i].mat_mul( M ) )
        G.add_edge( i, j, 1000 )

    return G


def get_dynkin_type( d_lst ):
    '''
    INPUT:
        - "d_lst" -- A list of lists of "Div" objects "d", 
                     such that d*d=-2 and d*(-3h+e1+...+er)=0 
                     where r=rank-1 and rank in [3,...,7].  
                     We assume that "is_root_basis(d_lst)==True":
                     linear independent, self intersection number -2
                     and pairwise product either 0 or 1.            
                     
    OUTPUT:
        - Returns a string denoting the Dynkin type of a 
          root system with basis "d_lst".  
          Returns 'A0' if "d_lst==[]".
    
    EXAMPLES:
        - [<1145>, <1123>, <23>, <45>, <56>, <78>] --> '3A1+A3'
          where 
          <1145> is shorthand for "Div.new('1145')".      
    '''
    if d_lst == []: return 'A0'

    key = "get_dynkin_type"
    if not key in nt.get_tool_dct():
        nt.p( 'Constructing list of Dynkin types...' )

        ade_lst = []
        for comb_lst in Combinations( 8 * ['A', 'D', 'E'], 8 ):
            for perm_lst in Permutations( comb_lst ):
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
            for r in range( 1, 8 + 1 ):
                for p_lst in Partitions( r + 8, length = 8 ):

                    # obtain type list
                    t_lst = [( ade[i], p_lst[i] - 1 ) for i in range( 8 ) if  p_lst[i] != 1]
                    t_lst.sort()

                    # obtain Root system
                    # or continue if invalid Cartan/Dynkin type
                    if ( 'D', 2 ) in t_lst or ( 'D', 3 ) in t_lst:
                        continue
                    try:
                        rs = RootSystem( t_lst )
                    except ValueError as err:
                        continue  # not a valid Cartan type

                    # obtain graph G
                    mat = list( -1 * rs.cartan_matrix() )
                    G = Graph()
                    G.add_vertices( range( len( mat ) ) );
                    for i in range( len( mat ) ):
                        for j in range( len( mat[0] ) ):
                           if mat[i][j] == 1:
                               G.add_edge( i, j )

                    # obtain string for type
                    # Example: [(A,1),(A,1),(A,1),(A,3)] ---> '3A1+A3'
                    tmp_lst = copy( t_lst )
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
                        nt.p( 'added to list: ', ts, '\t\t...please wait...' )

        nt.p( 'Finished constructing list of Dynkin types.' )
        # cache the constructed "type_lst"
        nt.get_tool_dct()[key] = type_lst
        nt.save_tool_dct()

    # end if

    type_lst = nt.get_tool_dct()[key]
    G1 = get_graph( d_lst )

    # loop through all types and check equivalence
    for ( G2, ts, t_lst ) in type_lst:
        if G1.is_isomorphic( G2 ):
            return ts

    return False


def get_orthogonal_roots( d_lst ):
    '''
    INPUT:       
        - "d_lst" -- A list of lists of "Div" objects "d", 
                     such that d*d=-2 and d*(-3h+e1+...+er)=0 
                     where r=rank-1 and rank in [3,...,7]. 
    OUTPUT:
        - Returns a list of "Div" objects, which represent 
          (-2)-classes of rank "r" 
          that are orthogonal to elements in "d_lst".
          
          See "get_m2_classes( r )" for specs of the (-2)-classes.
          For example '12', '1123', '14' are included in the returned list,
          but '-12', '-308' are not included.                
    '''
    m2_lst = get_m2_classes( d_lst[0].rank(), True )

    out_lst = []
    for m2 in m2_lst:
        if [m2 * d for d in d_lst] == len( d_lst ) * [0]:
            out_lst += [m2]

    return out_lst


def get_subspace_roots( d_lst ):
    '''
    INPUT:       
        - "d_lst" -- A list of lists of "Div" objects "d", 
                     such that d*d=-2 and d*(-3h+e1+...+er)=0 
                     where r=rank-1 and rank in [3,...,7]. 
    OUTPUT:
        - Returns a list of "Div" objects, which represent 
          (-2)-classes of rank "r" 
          that are contained in the subspace spanned by "d_lst".
          
          See "get_m2_classes( r )" for specs of the (-2)-classes.
          For example '12', '1123', '14' are included in the returned list,
          but '-12', '-308' are not included.                
    '''
    V = VectorSpace( QQ, d_lst[0].rank() )
    W = V.subspace( [d.e_lst for d in d_lst] )

    m2_lst = get_m2_classes( d_lst[0].rank(), True )

    out_lst = []
    for m2 in m2_lst:
        if vector( m2.e_lst ) in W:
            out_lst += [ m2 ]

    return out_lst


def is_equal_root_lst( d_lst1, d_lst2 ):
    '''
    Check whether "d_lst1" and "d_lst2"
    are bases of isomorphic root subsystems by using 
    "get_orthogonal_roots()" and "get_subspace_roots()".
    These methods return invariants for root subsystems.
    
    See [Proposition 3, http://arxiv.org/abs/1302.6678] for more info. 
    
    INPUT:
        - "d_lst1" -- A list of lists of "Div" objects "d", 
                      such that d*d=-2 and d*(-3h+e1+...+er)=0 
                      where r=rank-1 and rank in [3,...,7]. 
        - "d_lst2" -- Same as "d_lst1".
    OUTPUT:
        - True if "d_lst1" and "d_lst2" are equivalent
          as root sub systems in the root system   
          with Dynkin type either 
          
              A1, A1+A2, A4, D5, E6, E7 or E8.
          
          These root systems live in a subspace of an 
          (rank)-inner-product space with signature (1,rank-1).
          The subspace is the (rank-1)-space orthogonal to 
          -3h+e1+...+er.
    '''
    # ``rss'' is short hand for ``root subsystem''

    # check cardinality
    if len( d_lst1 ) != len( d_lst2 ):
        return False

    # empty root bases are equivalent
    if len( d_lst1 ) == 0:
        return True

    # check rank
    if d_lst1[0].rank() != d_lst2[0].rank():
        return False

    # check number of indecomposable classes of conics
    nfam1 = len( get_fam_classes( d_lst1[0].rank(), True, d_lst1 ) )
    nfam2 = len( get_fam_classes( d_lst2[0].rank(), True, d_lst2 ) )
    if nfam1 != nfam2:
        return False

    # check whether Graphs of rss are isomorphic
    G1 = get_graph( d_lst1 )
    G2 = get_graph( d_lst2 )
    if not G1.is_isomorphic( G2 ):
        return False

    # check whether the cardinality of the
    # roots orthoginal to d_lst# agree
    o_lst1 = get_orthogonal_roots( d_lst1 )
    o_lst2 = get_orthogonal_roots( d_lst2 )
    if len( o_lst1 ) != len( o_lst2 ):
        return False

    # check whether the cardinality of the
    # roots in subspace spanned by d_lst# agree
    s_lst1 = get_subspace_roots( d_lst1 )
    s_lst2 = get_subspace_roots( d_lst2 )
    if len( s_lst1 ) != len( s_lst2 ):
        return False

    return True


def get_root_bases( rank ):
    '''
    INPUT: 
        - "rank" -- An integer between 3 and 9.
    OUTPUT:
        - Returns a list of lists of "Div" objects "d", 
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
          
          The roots in the basis are all positive
          and thus of the form <ij>, <1ijk>, <2ij>, <30i>
          with i<j<k. For example '15' and '1124' 
          but not '-15' or '-1124' 
          (see "Div.get_label()" for notation).          
    '''
    key = 'get_root_bases_' + str( rank )

    # already computed before?
    if key in nt.get_tool_dct(): return nt.get_tool_dct()[key]

    nt.p( 'Constructing root bases for rank', rank, '...' )

    # Loop through all subsets of (-2)-classes of length at most rank-1.
    d_lst_lst = [[]]
    m2_lst = get_m2_classes( rank, True )
    for r in range( 1, rank ):
        nt.p( r, '/', rank - 1, ', length list =', len( m2_lst ), ', rank =', rank )
        for idx_lst in Subsets( range( len( m2_lst ) ), r ):

            # construct sub-list
            d_lst1 = [ m2_lst[idx] for idx in idx_lst ]

            # add if root basis
            if is_root_basis( d_lst1 ):
                d_lst1.sort( reverse = True )
                d_lst_lst += [d_lst1]

    # cache output
    d_lst_lst.sort( key = lambda d_lst: get_dynkin_type( d_lst ) )
    nt.get_tool_dct()[key] = d_lst_lst
    nt.save_tool_dct()

    return d_lst_lst



def get_cls_root_bases( max_rank = 9 ):
    '''
    See [Algorithm 5, http://arxiv.org/abs/1302.6678] for more info. 
    
    INPUT:
        - "max_rank" -- An integer in [3,...,9].
    
    OUTPUT:
        - A dictionary "bases_cls_dct" such that 
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
    for rank in range( max_rank, 3 - 1, -1 ):
        key = 'get_cls_root_bases_' + str( rank )
        if key in nt.get_tool_dct():
            return nt.get_tool_dct()[key]
    key = 'get_cls_root_bases_' + str( max_rank )


    Z1 = [ 12, 23, 34, 45, 56, 67, 78, 1123 ]
    Z2 = [ 12, 23, 34, 45, 56, 67, 78, 1123, 1145, 1347, 1678, 1127, 1456, 1567, 234, 278, 308 ]
    Z3 = [ 1123, 1345, 1165, 1285, 1673, 1274, 1684, 1178 ]
    Z0 = [ 12, 23, 34, 45, 56, 67, 78, 1123, -1145, -1345, -1167, -1178, -278, -218, -308, 218 ]
    Z_lst = [Z1, Z2, Z3, Z0]

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
            nt.p( 'rank =', rank )
            nt.p( 'Z before =', Z )
            Z = [ Div.new( str( z ), rank ) for z in Z if rank >= Div.get_min_rank( str( z ) )]
            nt.p( 'Z after  =', Z )
            for i in range( 1, rank ):

                nt.p( '\trank subsystem =', i, '\trank =', rank, )
                for idx_lst in Subsets( range( len( Z ) ), i ):

                    # recover subset of Z from indices
                    d_lst1 = [ Z[idx] for idx in idx_lst ]

                    # check whether d_lst1 is a root basis
                    if not is_root_basis( d_lst1 ):
                        continue

                    # check whether d_lst1 is new
                    new_d_lst = True
                    for d_lst2 in d_lst_lst:
                        if is_equal_root_lst( d_lst1, d_lst2 ):
                            new_d_lst = False
                            break

                    # add if new d_lst is found
                    if new_d_lst:
                        d_lst_lst += [d_lst1]

        # add list to dictionary
        bases_cls_dct[rank] = d_lst_lst

    # cache output
    nt.get_tool_dct()[key] = bases_cls_dct
    nt.save_tool_dct()

    return bases_cls_dct










