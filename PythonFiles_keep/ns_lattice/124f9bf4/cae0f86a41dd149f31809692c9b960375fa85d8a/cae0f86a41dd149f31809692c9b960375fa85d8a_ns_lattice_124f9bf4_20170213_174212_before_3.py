'''
Created on Aug 15, 2016
@author: Niels Lubbes

This module is for classifying real structures and singularities 
of weak Del Pezzo surfaces of degree between 1 and 7.

'''
from sage.all import *

from div_set import *
from dp_root_bases import *
from dp_involutions import *

from class_ns_tools import NSTools
from class_div import Div

nt = NSTools()


class DPLattice:
    '''
    Represents an equivalence class of the Neron-Severi lattice 
    of a real weak del Pezzo surface, together with an involution "M"
    and a set of effective (-2)-classes "d_lst". The effective (-2)-classes
    form the basis of a root system.
    
        ( ZZ<h,e1,...,er>, M, d_lst )
    
    From these objects it is possible to compute the remaining attributes of 
    this class. 
    
    If <h,e1,...,er> is a basis for the Neron-Severi lattice of the 
    projective plane P^2 blown up in r points then the the canonical 
    class k equals 
        k=-3h+e1+...+er.
    The intersection product is in this case -h^2=e1^2=...=er^2=-1 with
    remaining intersections zero.
    
    Otherwise if <h,e1,...,er> is a basis for the Neron-Severi lattice of the 
    P^1xP^1 blown up in r points then the the canonical 
    class k equals 
        k=-2*(h+e1).
    The intersection product is in this case -h*e1=e2^2=...=er^2=-1 with
    remaining intersections zero.         
    '''


    def __init__( self ):
        '''
        Constructor.
        '''

        #
        # A matrix which correspond to an
        # involution of the lattice
        #     <h,e1,...,er>
        # with r=rank-1 and 2 <= r <= 8.
        #
        self.M = None

        #
        # A list of "Div" objects that
        # correspond to the eigenvectors
        # of eigenvalue 1 of M.
        # These "Div" objects form a basis of
        # a root subsystem.
        #
        self.Md_lst = None

        #
        # A String that denotes the  Dynkin type of "Md_lst".
        #
        self.Mtype = None

        #
        # A list of "Div" objects d such that
        # d*d==-2 and d*k=0
        # where k denotes the canonical class.
        #
        # These elements represent effective
        # (-2)-classes.
        #
        self.d_lst = None

        #
        # A String that denotes the Dynkin type of "d_lst".
        #
        self.type = None

        #
        # A list of "Div" objects "m" such
        # that
        #        m*m==-1==m*k
        # and
        #        m*d>=0
        # for all d in d_lst, where k denotes
        # the canonical class.
        #
        # These elements represent (-1)-classes
        # that cannot be written as the sum of
        # two effective classes. In other words,
        # the classes are indecomposable.
        #
        self.m1_lst = None

        #
        # A list of "Div" objects "f" such
        # that f*f==0, f*(-k)==2
        # and m*d>=0 for all d in d_lst,
        # where k denotes the canonical class.
        #
        self.fam_lst = None

        #
        # A list "Div" objects that represent
        # indecomposable and real (-2)-classes.
        # Thus these classes are send to itself by M.
        #
        # Geometrically these classes correspond to
        # real isolated singularities.
        #
        self.real_d_lst = None

        #
        # A list "Div" objects that represent
        # indecomposable and real (-1)-classes.
        # Thus these classes are send to itself by M.
        #
        # Geometrically these classes correspond
        # to real lines.
        #
        self.real_m1_lst = None

        #
        # A list "Div" objects that represent
        # real classes in "self.fam_lst".
        # Thus these classes are send to itself by M.
        #
        # Geometrically these classes correspond to
        # a real families of conics
        #
        self.real_fam_lst = None


    def get_rank( self ):
        '''
        INPUT:
            - "self" -- We expect self.M != None.
        OUTPUT:
            - Integer denoting rank of lattice.
        '''
        return self.M.dimensions()[0]


    def get_degree( self ):
        '''
        INPUT:
            - "self" -- We expect self.M != None.        
        OUTPUT:
            - Integer denoting the degree of weak del Pezzo surface with
              "self" the corresponding Neron-Severi lattice.
        '''
        return 10 - self.get_rank()


    def get_numbers( self ):
        '''
        INPUT:
            - "self" --
        OUTPUT:
            - List of 6 integers:
                
                0: #indecomposable (-2)-classes 
                1: #indecomposable (-1)-classes
                2: #families of conics
                
                3: #real effective (-2)-classes 
                4: #real indecomposable (-1)-classes
                5: #real families of conics                
            
            where # stands for number of.
            
            Note that a divisor class is indecomposable 
            if it is effective and cannot be written as 
            the sum of two effective classes.
        '''
        return ( len( self.d_lst ),
                 len( self.m1_lst ),
                 len( self.fam_lst ),
                 len( self.real_d_lst ),
                 len( self.real_m1_lst ),
                 len( self.real_fam_lst ) )


    def change_basis( self, B ):
        '''
        INPUT:
            
            - "self" -- "DPLattice" object.
            
            - "B"    -- A matrix whose rows correspond to generators of 
                        a new basis. We assume that the intersection
                        matrix for this basis is the default
                        diagonal matrix with diagonal (1,-1,...,-1).
        OUTPUT:
        
            - A new "DPLattice" object, which represents the current  
              lattice with respect to a new basis.
                
        '''
        dpl = DPLattice()
        dpl.M = ~( B.T ) * self.M * ( B.T )  # ~B is inverse of B
        dpl.Md_lst = [ Md.change_basis( B ) for Md in self.Md_lst ]
        dpl.Mtype = self.Mtype
        dpl.d_lst = [ d.change_basis( B ) for d in self.d_lst ]
        dpl.type = self.type
        dpl.m1_lst = [ m1.change_basis( B ) for m1 in self.m1_lst ]
        dpl.fam_lst = [ fam.change_basis( B ) for fam in self.fam_lst ]
        dpl.real_d_lst = [ d.change_basis( B ) for d in self.real_d_lst ]
        dpl.real_m1_lst = [ m1.change_basis( B ) for m1 in self.real_m1_lst ]
        dpl.real_fam_lst = [ fam.change_basis( B ) for fam in self.real_fam_lst ]

        return dpl


    @staticmethod
    def init( d_lst, Md_lst, M ):
        '''
        INPUT:
            - "d_lst"  -- A list of Div objects of rank 2<=r<=9,
                          such that the matrix of the intersection 
                          product is the default diagonal matrix with 
                          signature (1,r).
                            
            - "Md_lst" -- A list of Div objects of rank r,
                          such that the matrix of the intersection 
                          product is the default diagonal matrix with 
                          signature (1,r).  
            
            - "M"      -- An r*r unimodular involutary matrix whose 
                          eigenspace for -1 is generated by "Md_lst"
                          and M(d_lst)=d_lst.
        OUTPUT:
            - "" -- A DPLattice class whose attributes are set 
                    according to input:
                        * DPLattice.M
                        * DPLattice.Md_lst
                        * DPLattice.d_lst
                    The remaining attributes of DPLattice can be computed 
                    from these attributes.
        '''
        dpl = DPLattice()

        dpl.M = M
        dpl.Md_lst = Md_lst
        dpl.Mtype = get_dynkin_type( Md_lst )
        dpl.type = get_dynkin_type( d_lst )

        dpl.d_lst = d_lst
        dpl.m1_lst = get_m1_classes( dpl.get_rank(), True, d_lst )
        dpl.fam_lst = get_fam_classes( dpl.get_rank(), True, d_lst )

        dpl.real_d_lst = [ d for d in dpl.d_lst if d.mat_mul( M ) == d ]
        dpl.real_m1_lst = [ m1 for m1 in dpl.m1_lst if m1.mat_mul( M ) == m1 ]
        dpl.real_fam_lst = [ f for f in dpl.fam_lst if f.mat_mul( M ) == f ]

        return dpl


    @staticmethod
    def get_cls_real_dp( max_rank = 7, provable = True ):
        '''
        See [http://arxiv.org/abs/1302.6678] for more info.
    
        INPUT:
            - "max_rank" -- An integer in [3,...,9].
            - "provable" -- A boolean.
    
        OUTPUT:
            - A dictionary "cls_dct" such that 
              "cls_dct[rank]" is a list of DPLattice
              objects corresponding the enhanced 
              Neron-Severi lattice of weak Del Pezzo
              surfaces of degree (10-rank). 
              
              All the Div objects referenced in 
              the DPLattice objects of the output
              have the default intersection matrix:
              diagonal matrix with diagonal: 
                  (1,-1,...,-1). 
                            
              We classify for rank in [3,...,max_rank].
              For rank 8 and 9 this classification method 
              will not terminate within reasonable time.
        
              If "provable==True" then a slow version
              of the classification algorithm will be used.
              Otherwise, a faster version will be used 
              which has the advantage that the number of 
              different involutions M is minimized.  
        '''
        key = 'get_cls_real_dp'
        if not provable:
            key += '_' + str( provable )

        if key in nt.get_tool_dct():
            return nt.get_tool_dct()[key]

        nt.p( 'max_rank =', max_rank, ', provable =', provable )
        dp_cls_dct = {}
        for rank in range( 3, max_rank + 1 ):
            dpl_lst = []
            nt.p( 'rank =', rank )

            if provable:
                #
                # slow version of algorithm
                #
                for d_lst in get_cls_root_bases( max_rank )[rank]:
                    nt.p( 'd_lst =', d_lst )
                    for ( M, Md_lst ) in get_involutions( rank ):

                        # check whether involution M preserves d_lst
                        dm_lst = [ d.mat_mul( M ) for d in d_lst ]
                        if sorted( dm_lst ) != sorted( d_lst ):
                            continue

                        # setup DPLattice object
                        dpl = DPLattice.init( d_lst, Md_lst, M )

                        # add to classification if not equivalent to objects in list
                        # see "DPLattice.__eq__(self)".
                        if dpl not in dpl_lst:
                            dpl_lst += [dpl]
            else:
                #
                # fast version of algorithm with nice representatives of dpl's
                #
                for ( M, Md_lst ) in get_cls_involutions( max_rank )[rank]:
                    nt.p( 'Md_lst =', Md_lst )
                    for d_lst in get_root_bases( rank ):

                        # check whether involution M preserves d_lst
                        dm_lst = [ d.mat_mul( M ) for d in d_lst ]
                        if sorted( dm_lst ) != sorted( d_lst ):
                            continue

                        # setup DPLattice object
                        dpl = DPLattice.init( d_lst, Md_lst, M )

                        # add to classification if not equivalent to objects in list
                        # see "DPLattice.__eq__(self)".
                        if dpl not in dpl_lst:
                            dpl_lst += [dpl]

            # end of classification for given rank.
            # add to classification dictionary
            dp_cls_dct[rank] = dpl_lst

        # store classification
        nt.get_tool_dct()[key] = dp_cls_dct
        nt.save_tool_dct()

        return dp_cls_dct


    @staticmethod
    def get_tex_table( cls_dct ):
        '''
        INPUT: 
            - "cls_dct" -- A dictionary with each key an integer 
                           corresponding to rank and each value 
                           corresponds to a list of DPLattice objects
                           of given rank.  
        OUTPUT:
            - A String in Tex format, representing a table of "cls_dct"
        '''

        tex = '''
\\renewcommand*{\\arraystretch}{1.2}
\\begin{longtable}{|@{}c@{}||@{~}c@{~}|@{~}l@{~}|l|l|l|l|}    
\\hline
 & $\\lambda,d,n$ & $\\sigma_*$ & $\\McalB(X)$ & $\\McalE(X)$ & $\\McalF(X)$ & Description 
\\\\\\hline\\hline
\\endhead'''

        abbr = True  # True if divisor classes should be abbreviated
        col_len = [10, 15, 15]  # bound for character length of column
        real_tex = '\\underline'  # Tex command for displaying real classes

        row_idx = 1
        for rank in [4, 6]:
            for dpl in cls_dct[rank]:

                # strings for first 3 columns
                #
                col0 = '$' + str( row_idx ) + '$'

                col1 = '$'
                col1 += str( len( dpl.real_fam_lst ) ) + ', '
                col1 += str( dpl.get_degree() ) + ', '
                col1 += str( dpl.get_degree() - 1 )
                col1 += '$'

                col2 = ( '$' + str( dpl.Mtype ) + '$' ).replace( 'A', 'A_' ).replace( 'D', 'D_' )

                tex += '\n'
                tex += col0 + ' & '
                tex += col1 + ' & '
                tex += col2

                # sort elements, such that adjacent elements
                # are conjugates.
                #
                lst1_lst = [ dpl.d_lst, dpl.m1_lst, dpl.fam_lst]
                lst2_lst = []
                for lst1 in lst1_lst:
                    lst2 = []
                    for elt1 in lst1:
                        for elt2 in [elt1, elt1.mat_mul( dpl.M )]:
                            if elt2 not in lst2:
                                lst2 += [elt2]
                    lst2_lst += [lst2]


                # sort elements on string length
                lst3_lst = []
                col_idx = 0
                for lst2 in lst2_lst:
                    lst3 = []
                    idx = 0
                    while idx < len( lst2 ):
                        s = ''
                        len_s = 0
                        while idx < len( lst2 ) and len_s <= col_len[col_idx]:

                            # get non abbreviated label
                            ts = lst2[idx].get_label( abbr )

                            # display real divisors in bold
                            real_div = ( lst2[idx].mat_mul( dpl.M ) == lst2[idx] )
                            if real_div:
                                ts = real_tex + '{' + ts + '}'
                            s += '$' + ts + '$, '

                            # increase index for lst2
                            idx += 1

                            # determine length of next string
                            len_s = len( s.replace( real_tex + '{', '' ).replace( '}', '' ).replace( '$', '' ).replace( ',', '' ) )
                            if idx < len( lst2 ):
                                len_s += len( lst2[idx].get_label( abbr ) )

                        lst3 += [s]
                    if len( lst3 ) > 0 and lst3[-1].endswith( ', ' ):
                        lst3[-1] = lst3[-1][:-2]
                    lst3_lst += [lst3]
                    col_idx += 1
                max_len3 = max( [len( lst3 ) for lst3 in lst3_lst ] )


                # col3, col4, col5, col6
                tex += '\n     &'
                for i in range( 0, max_len3 ):
                    if i > 0:
                        tex += ' & & & '

                    for lst3 in lst3_lst:
                        if i == 0 and lst3 == []:
                            tex += '$\\emptyset$'
                        if i < len( lst3 ):
                            tex += lst3[i]
                        tex += ' & '

                    # description column here
                    tex += '\n\\\\'
                tex += '\\hline'
                row_idx += 1
            # end for dpl

            tex += '\\hline'
            tex += '\n'

        # end for rank
        tex += '\\end{longtable}'

        return tex



    # overloading of "=="
    def __eq__( self, other ):

        # Dynkin type real structures agree?
        if self.Mtype != other.Mtype:
            return False

        # Dynkin type effective (-2)-classes agree?
        if self.type != other.type:
            return False

        # cardinality of classes agree?
        if len( self.d_lst ) != len( other.d_lst ):
            return False
        if len( self.m1_lst ) != len( other.m1_lst ):
            return False
        if len( self.fam_lst ) != len( other.fam_lst ):
            return False
        if len( self.real_d_lst ) != len( other.real_d_lst ):
            return False
        if len( self.real_m1_lst ) != len( other.real_m1_lst ):
            return False
        if len( self.real_fam_lst ) != len( other.real_fam_lst ):
            return False

        # check incidence graphs
        all_m1_lst = get_m1_classes( self.get_rank(), True )
        G1 = get_ext_graph( self.d_lst + all_m1_lst, self.M )
        G2 = get_ext_graph( other.d_lst + all_m1_lst, other.M )
        if not G1.is_isomorphic( G2, edge_labels = True ):
            nt.p( 'Non isomorphic graphs (unexpected position): ', self, other )
            return False

        # check incidence graphs including fam_lst classes
        G1 = get_ext_graph( self.d_lst + all_m1_lst + self.fam_lst, self.M )
        G2 = get_ext_graph( other.d_lst + all_m1_lst + other.fam_lst, other.M )
        if not G1.is_isomorphic( G2, edge_labels = True ):
            nt.p( 'Non isomorphic graphs including fam_lst (unexpected position): ', self, other )
            return False

        return True


    # operator overloading for <
    # Used for sorting lists of DPLattice objects:
    #     <http://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes-in-python>
    def __lt__( self, other ):

        if self.get_rank() != other.get_rank():
           return self.get_rank() < other.get_rank()

        if self.get_degree() != other.get_degree():
           return self.get_degree() < other.get_degree()

        if len( self.real_fam_lst ) != len( other.real_fam_lst ):
            return len( self.real_fam_lst ) < len( other.real_fam_lst )

        if self.type != other.type:
            return self.type < other.type

        if self.Mtype != other.Mtype:
            return self.type < other.type

        if len( self.fam_lst ) != len( other.fam_lst ):
            return len( self.fam_lst ) < len( other.fam_lst )

        if len( self.m1_lst ) != len( other.m1_lst ):
            return len( self.m1_lst ) < len( other.m1_lst )



    # overloading of "str()": human readable string representation of object
    def __str__( self ):

        s = '\n'
        s += 50 * '=' + '\n'

        s += 'Degree          = ' + str( self.get_degree() ) + '\n'
        s += 'Rank            = ' + str( self.get_rank() ) + '\n'
        s += 'Intersection    = ' + str( list( self.m1_lst[0].int_mat ) ) + '\n'
        s += 'Real structure  = ' + str( self.Mtype ) + '\n'
        s += 'Singularities   = ' + str( self.type ) + '\n'

        arrow = '  --->  '

        s += 'Real involution:\n'
        b_lst = [Div( row ) for row in identity_matrix( ZZ, self.get_rank() ).rows() ]
        for b in b_lst:
            s += '\t' + str( b ) + arrow + str( b.mat_mul( self.M ) ) + '\n'

        s += 'Indecomposable (-2)-classes:\n'
        for d in self.d_lst:
            s += '\t' + str( d ) + arrow + str( d.mat_mul( self.M ) ) + '\n'
        s += '\t#real = ' + str( len( self.real_d_lst ) ) + '\n'

        s += 'Indecomposable (-1)-classes:\n'
        for m1 in self.m1_lst:
            s += '\t' + str( m1 ) + arrow + str( m1.mat_mul( self.M ) ) + '\n'
        s += '\t#real = ' + str( len( self.real_m1_lst ) ) + '\n'

        s += 'Classes of conical families:\n'
        for fam in self.fam_lst:
            s += '\t' + str( fam ) + arrow + str( fam.mat_mul( self.M ) ) + '\n'
        s += '\t#real = ' + str( len( self.real_fam_lst ) ) + '\n'

        s += 50 * '=' + '\n'

        return s


