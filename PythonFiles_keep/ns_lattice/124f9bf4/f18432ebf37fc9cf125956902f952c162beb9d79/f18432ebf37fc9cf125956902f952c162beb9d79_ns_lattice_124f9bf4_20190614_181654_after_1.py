'''
Created on Aug 15, 2016
@author: Niels Lubbes

This module is for classifying real structures and singularities 
of weak Del Pezzo surfaces of degree between 1 and 7.

'''
import time

from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_Subsets
from ns_lattice.sage_interface import sage_VectorSpace
from ns_lattice.sage_interface import sage_vector

from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_indecomp_divs
from ns_lattice.div_in_lattice import get_ak

from ns_lattice.dp_root_bases import get_graph
from ns_lattice.dp_root_bases import get_ext_graph
from ns_lattice.dp_root_bases import get_dynkin_type
from ns_lattice.dp_root_bases import convert_type
from ns_lattice.dp_root_bases import get_root_bases_orbit
from ns_lattice.dp_root_bases import is_root_basis

from ns_lattice.dp_involutions import basis_to_involution
from ns_lattice.dp_involutions import is_integral_involution

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_div import Div

from ns_lattice.class_eta import ETA


class DPLattice:
    '''
    Represents an equivalence class of the Neron-Severi lattice 
    of a real weak del Pezzo surface, together with an involution "M"
    and a set of effective (-2)-classes "d_lst". The effective (-2)-classes
    form the basis of a root system.
    
        ( ZZ<e0,e1,...,er>, M, d_lst )
    
    From these objects it is possible to compute the remaining attributes of 
    this class. 
    
    If <e0,e1,...,er> is a basis for the Neron-Severi lattice of the 
    projective plane P^2 blown up in r points then the the canonical 
    class k equals 
        k=-3e0+e1+...+er.
    The intersection product is in this case -e0^2=e1^2=...=er^2=-1 with
    remaining intersections zero.
    
    Otherwise if <e0,e1,...,er> is a basis for the Neron-Severi lattice of the 
    P^1xP^1 blown up in r points then the the canonical 
    class k equals 
        k=-2*(e0+e1).
    The intersection product is in this case -h*e1=e2^2=...=er^2=-1 with
    remaining intersections zero.         
    

    Attributes
    ----------
    M : sage_matrix<sage_ZZ>
        A matrix which correspond to an involution of the lattice
        <e0,e1,...,er> with r=rank-1 and 2 <= r <= 8.
    
    Md_lst : list<Div>
        A list of "Div" objects that correspond to the eigenvectors
        of eigenvalue 1 of M. These "Div" objects form a basis of
        a root subsystem.

    Mtype : string
        A String that denotes the  Dynkin type of "Md_lst".
        
    d_lst : list<Div>
        A list of "Div" objects d such that d*d==-2 and d*k=0
        where k denotes the canonical class. These elements 
        represent effective (-2)-classes.

    type : string
        A String that denotes the Dynkin type of "d_lst".
 
    m1_lst : list<Div>
        A list of "Div" objects "m" such that
        m*m==-1==m*k and m*d>=0 for all d in d_lst, 
        where k denotes the canonical class.        
        These elements represent (-1)-classes that cannot be written 
        as the sum of two effective classes. 
        In other words, the classes are indecomposable.
        
    fam_lst : list<Div>
        A list of "Div" objects "f" such that 
        f*f==0, f*(-k)==2 and m*d>=0 
        for all d in d_lst, where k denotes the canonical class.
                
    real_d_lst : list<Div>
        A list "Div" objects that represent indecomposable and 
        real (-2)-classes. Thus these classes are send to itself by M.
        Geometrically these classes correspond to real isolated singularities.
        
        
    real_m1_lst : list<Div>
        A list "Div" objects that represent indecomposable and 
        real (-1)-classes. Thus these classes are send to itself by M.
        Geometrically these classes correspond to real lines.
        
        
    self.real_fam_lst : list<Div>
        A list "Div" objects that represent real classes in "self.fam_lst".
        Thus these classes are send to itself by M.
        Geometrically these classes correspond to a real families of conics.        
   
    self.or_lst : list<Div>
        A list of "Div" objects that represents roots that are orthogonal to
        "self.d_lst".  

    self.sr_lst : list<Div>
        A list of "Div" objects that represents roots that are contained in
        the subspace spanned by "self.d_lst".  
    
    self.G : sage_Graph
        The Cremona invariant for the current lattice.
    '''

    def __init__( self, d_lst, Md_lst, M ):
        '''
        Constructor.
        
        Returns
        -------
        DPLattice
            A DPLattice class whose attributes are set according to input:
                * DPLattice.M
                * DPLattice.Md_lst
                * DPLattice.d_lst
            The remaining attributes of DPLattice can be computed 
            from these attributes.
                    
            In order for this object to make sense, it is required that the 
            involution "M" preserves "d_lst" as a set. Geometrically this 
            means that the involution sends isolated singularities to isolated 
            singularities.  
        '''

        self.d_lst = d_lst
        self.Md_lst = Md_lst
        self.M = M

        self.m1_lst = None
        self.fam_lst = None
        self.real_d_lst = None
        self.real_m1_lst = None
        self.real_fam_lst = None
        self.Mtype = None
        self.type = None
        self.or_lst = None
        self.sr_lst = None
        self.G = None


    def set_attributes( self, level = 9 ):
        '''
        Sets attributes of this object, depending
        on the input level.
        For constructing a classification we instantiate
        many DPLattice objects. This method allows us 
        to minimize the number of attributes that computed
        (thus we use lazy evaluation).
        
        Parameter
        ---------
        self: DPLattice
            At least self.M, self.Md_lst and self.d_lst        
            should be initialized.
        
        level : int
            A non-negative number.
        '''

        # M, Md_lst and d_lst are set.

        if self.m1_lst == None:
            all_m1_lst = get_divs( get_ak( self.get_rank() ), 1, -1, True )
            self.m1_lst = get_indecomp_divs( all_m1_lst, self.d_lst )

        if level < 1: return

        if self.fam_lst == None:
            all_fam_lst = get_divs( get_ak( self.get_rank() ), 2, 0, True )
            self.fam_lst = get_indecomp_divs( all_fam_lst, self.d_lst )

        if level < 2: return

        if self.real_d_lst == None:
            self.real_d_lst = [ d for d in self.d_lst if d.mat_mul( self.M ) == d ]

        if level < 3: return

        if self.real_m1_lst == None:
            self.real_m1_lst = [ m1 for m1 in self.m1_lst if m1.mat_mul( self.M ) == m1 ]

        if level < 4: return

        if self.real_fam_lst == None:
            self.real_fam_lst = [ f for f in self.fam_lst if f.mat_mul( self.M ) == f ]

        if level < 5: return

        if self.or_lst == None:
            self.or_lst = []
            for m2 in get_divs( get_ak( self.get_rank() ), 0, -2, True ):
                if [m2 * d for d in self.d_lst] == len( self.d_lst ) * [0]:
                    self.or_lst += [m2]

        if level < 6: return

        if self.sr_lst == None:
            V = sage_VectorSpace( sage_QQ, self.get_rank() )
            W = V.subspace( [d.e_lst for d in self.d_lst] )
            self.sr_lst = []
            for m2 in get_divs( get_ak( self.get_rank() ), 0, -2, True ):
                if sage_vector( m2.e_lst ) in W:
                    self.sr_lst += [ m2 ]

        if level < 7: return

        if self.type == None:
            self.type = get_dynkin_type( self.d_lst )

        if level < 8: return

        if self.Mtype == None:
            self.Mtype = get_dynkin_type( self.Md_lst )

        if level < 9: return

        if self.G == None:
            self.G = get_ext_graph( self.d_lst + self.m1_lst, self.M )




    def get_rank( self ):
        '''
        Parameters
        ----------
        self : DPLattice
            We expect self.M != None.
        
        Returns
        -------
        int
            Integer denoting rank of lattice.
        '''
        return self.M.dimensions()[0]


    def get_degree( self ):
        '''
        Parameters
        ----------
        self : DPLattice
            We expect self.M != None.        
        
        Returns
        -------
        int
            Integer denoting the degree of weak del Pezzo surface with
            "self" its corresponding Neron-Severi lattice.
        '''
        return 10 - self.get_rank()


    def get_numbers( self ):
        '''
        Parameters
        ----------
        self : DPLattice
        
        Returns
        -------
        list<int>
            List of 6 integers:
                
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
        self.set_attributes( 6 )
        return ( len( self.d_lst ),
                 len( self.m1_lst ),
                 len( self.fam_lst ),
                 len( self.real_d_lst ),
                 len( self.real_m1_lst ),
                 len( self.real_fam_lst ) )


    def contains_fam_pair( self ):
        '''
        Parameters
        ----------
        self : DPLattice
        
        Returns
        -------
        bool
            True if self.real_fam_lst contains two Div classes 
            with intersection one. Geometrically this means that a 
            weak del Pezzo surface with a Neron-Severi lattice that
            is isomorphic to this one, must be birational to P1xP1
            (ie. fiber product of the projective line with itself).             
        '''
        self.set_attributes( 6 )
        for f1 in self.real_fam_lst:
            for f2 in self.real_fam_lst:
                if f1 * f2 == 1:
                    return True
        return False


    def is_real_minimal( self ):
        '''
        Parameters
        ----------
        self : DPLattice
        
        Returns
        -------
        bool
            True if self.m1_lst does not contain classes u and v 
            such that either  
            * u.mat_mul( self.M ) == v and u*v==0, or 
            * u.mat_mul( self.M ) == u.
            This means that self is the DPLattice of a 
            real-minimal weak del Pezzo surface. Thus no
            disjoint complex conjugate exceptional curves
            or real exceptional curves can be contracted.          
        '''
        self.set_attributes( 0 )
        for u in self.m1_lst:
            v = u.mat_mul( self.M )
            if v * u == 0 or v == u:
                return False
        return True


    def get_marked_Mtype( self ):
        '''
        We mark Mtype with a '-symbol to distinguish between real 
        structures of the same Dynkin type that are not conjugate.
        '''
        if self.get_degree() not in [6, 4, 2]:
            return self.Mtype

        self.set_attributes( 8 )
        if ( self.get_degree(), self.Mtype ) not in [ ( 6, 'A1' ), ( 4, '2A1' ), ( 2, '3A1' ) ]:
            return self.Mtype

        mark = ''
        if list( self.M.T[0] ) != [1] + ( self.get_rank() - 1 ) * [0]:
            # in this case e0 is not send to e0 by the involution self.M
            mark = "'"

        return self.Mtype + mark


    def get_real_type( self ):
        '''
        Gets the Dynkin type (self.type) of self.d_lst. 
        The components of the Dynkin diagram that are preserved by
        the involution induced by the real structure are marked. 
                 
        Returns
        -------
        string
            Dynkin types of components 
        '''
        comp_lst = get_graph( self.d_lst ).connected_components()
        comp_lst.reverse()  # smaller components first
        if comp_lst == []:
            return 'A0'

        # construct list of types
        type_lst = []
        for comp in comp_lst:
            c_lst = [ self.d_lst[i] for i in comp]
            mc_lst = [ c.mat_mul( self.M ) for c in c_lst ]
            mc_lst.sort()
            type = get_dynkin_type( c_lst )

            if set( mc_lst ) == set( c_lst ) and c_lst != []:
                type_lst += ['{' + type + '}']
            else:
                type_lst += [type]

        # construct string
        out = ''
        while type_lst != []:
            type = type_lst[0]
            num = type_lst.count( type )
            if num != 1: out += str( num )
            out += type + '+'
            type_lst = [ elt for elt in type_lst if elt != type ]
        out = out[:-1]  # remove last plus

        return out


    def get_basis_change( self, B ):
        '''
        Parameters
        ----------
        self : DPLattice
            
        B : sage_matrix<sage_ZZ>   
            A matrix whose rows correspond to generators of 
            a new basis. We assume that the intersection
            matrix for this basis is the default
            diagonal matrix with diagonal (1,-1,...,-1).
        
        Returns
        -------
        DPLattice
            A new "DPLattice" object, which represents the current  
            lattice with respect to a new basis.
                
        '''
        self.set_attributes( 6 )

        d_lst_B = [ d.get_basis_change( B ) for d in self.d_lst ]
        Md_lst_B = [ Md.get_basis_change( B ) for Md in self.Md_lst ]
        M_B = ~( B.T ) * self.M * ( B.T )  # ~B is inverse of B, new involution after coordinate change

        dpl = DPLattice( d_lst_B, Md_lst_B, M_B )
        dpl.Mtype = self.Mtype
        dpl.type = self.type
        dpl.m1_lst = [ m1.get_basis_change( B ) for m1 in self.m1_lst ]
        dpl.fam_lst = [ fam.get_basis_change( B ) for fam in self.fam_lst ]
        dpl.real_d_lst = [ d.get_basis_change( B ) for d in self.real_d_lst ]
        dpl.real_m1_lst = [ m1.get_basis_change( B ) for m1 in self.real_m1_lst ]
        dpl.real_fam_lst = [ fam.get_basis_change( B ) for fam in self.real_fam_lst ]

        return dpl


    @staticmethod
    def get_bas_lst( rank = 9 ):
        '''
        See [Algorithm 5, http://arxiv.org/abs/1302.6678] for more info. 
        
        Parameters
        ----------
        rank : int
            An integer in [3,...,9].    
        
        Returns
        -------
        list<DPLattice>
            A list of "DPLattice" objects dpl such that dpl.d_lst 
            is the bases of a root subsystem and dpl.Mtype == A0. 
            The list contains exactly one representative for all 
            root subsystems up to equivalence.  
             
            The list represents a classification of root 
            subsystems of the root system with Dynkin type either:
                A1, A1+A2, A4, D5, E6, E7 or E8,
            corresponding to ranks 3, 4, 5, 6, 7, 8 and 9 respectively 
            (eg. A1+A2 if rank equals 4, and E8 if rank equals 9).
            Note that the root systems live in a subspace of 
            the vector space associated to the Neron-Severi lattice 
            of a weak Del Pezzo surface.
        '''
        # check whether classification of root bases is in cache
        key = 'get_bas_lst__' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        NSTools.p( 'start' )

        A = [ 12, 23, 34, 45, 56, 67, 78]
        B = [ 1123, 1145, 1456, 1567, 1678, 278 ]
        C = [ 1127, 1347, 1567, 234, 278, 308 ]
        D = [ 1123, 1345, 1156, 1258, 1367, 1247, 1468, 1178 ]

        dpl_lst = []
        for ( lst1, lst2 ) in [ ( A, [] ), ( A, B ), ( A, C ), ( [], D ) ]:

            # restrict to divisors in list, that are of rank at most "max_rank"
            lst1 = [ Div.new( str( e ), rank ) for e in lst1 if rank >= Div.get_min_rank( str( e ) ) ]
            lst2 = [ Div.new( str( e ), rank ) for e in lst2 if rank >= Div.get_min_rank( str( e ) ) ]

            # the involution is trivial
            Md_lst = []
            M = sage_identity_matrix( sage_QQ, rank )

            # loop through the lists
            sub1 = sage_Subsets( range( len( lst1 ) ) )
            sub2 = sage_Subsets( range( len( lst2 ) ) )
            eta = ETA( len( sub1 ) * len( sub2 ), 20 )
            for idx2_lst in sub2:
                for idx1_lst in sub1:

                    eta.update( 'get_bas_lst rank =', rank )

                    d_lst = [ lst1[idx1] for idx1 in idx1_lst ]
                    d_lst += [ lst2[idx2] for idx2 in idx2_lst ]

                    if not is_root_basis( d_lst ):
                        continue

                    dpl = DPLattice( d_lst, Md_lst, M )

                    if dpl not in dpl_lst:
                        dpl.set_attributes()
                        dpl_lst += [dpl]

        # cache output
        dpl_lst.sort()
        NSTools.get_tool_dct()[key] = dpl_lst
        NSTools.save_tool_dct()

        return dpl_lst


    @staticmethod
    def get_inv_lst( rank = 9 ):
        '''
        Outputs a list representing a classification of root 
        subsystems that define unimodular involutions on the 
        Neron-Severi lattice of a weak del Pezzo surface.
        We consider root subsystems of the root system with Dynkin 
        type either:
            A1, A1+A2, A4, D5, E6, E7 or E8,
        corresponding to ranks 3, 4, 5, 6, 7, 8 and 9 respectively 
        (eg. A1+A2 if rank equals 4, and E8 if rank equals 9).
        Note that root systems live in a subspace of 
        the vector space associated to the Neron-Severi lattice 
        of a weak Del Pezzo surface.        
        
                
        Parameters
        ----------
        max_rank : int
            An integer in [3,...,9].           
    
        Returns
        -------
        list<DPLattice>
            A list of "DPLattice" objects dpl such that dpl.Md_lst 
            is the bases of a root subsystem and dpl.type == A0. 
            The list contains exactly one representative for 
            root subsystems up to equivalence, so that the root
            subsystem defines a unimodular involution.  
        '''
        # check cache
        key = 'get_inv_lst__' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        bas_lst = DPLattice.get_bas_lst( rank )

        NSTools.p( 'start' )

        inv_lst = []
        eta = ETA( len( bas_lst ), 1 )
        for bas in bas_lst:
            eta.update( bas.type )

            M = basis_to_involution( bas.d_lst, rank )
            if not is_integral_involution( M ):
                continue
            inv = DPLattice( [], bas.d_lst, M )
            inv.set_attributes()

            # real structures with different Dynkin types may be equivalent
            if inv not in inv_lst:
                inv_lst += [ inv ]
            else:
                NSTools.p( 'Found ambitious type for real structure:', bas.type )

        # store in cache
        inv_lst.sort()
        NSTools.get_tool_dct()[key] = inv_lst
        NSTools.save_tool_dct()

        return inv_lst


    @staticmethod
    def get_cls_slow( rank = 7 ):
        '''        
        Use get_cls_real_dp() for a faster method. This method does not terminate
        within reasonable time if rank>7. We still keep the method in order to 
        compare the outcomes in case rank<=9.
        
        Parameters
        ----------
        max_rank : int
            An integer in [3,...,9].           
    
        Returns
        -------
        list<DPLattice>
            A list of DPLattice objects corresponding to Neron-Severi lattices 
            of weak Del Pezzo surfaces of degree (10-rank). The list contains
            exactly one representative for each equivalence class.
              
            All the Div objects referenced in the DPLattice objects of 
            the output have the default intersection matrix:
                diagonal matrix with diagonal: (1,-1,...,-1). 
        '''
        # check cache
        key = 'get_cls_slow__' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        inv_lst = DPLattice.get_inv_lst( rank )
        bas_lst = DPLattice.get_bas_lst( rank )


        # we fix an involution up to equivalence and go through
        # all possible root bases for singularities.
        dpl_lst = []
        eta = ETA( len( bas_lst ) * len( inv_lst ), 20 )
        for inv in inv_lst:
            for bas in bas_lst:

                orbit_lst = get_root_bases_orbit( bas.d_lst )
                eta.update( 'len( orbit_lst ) =', len( orbit_lst ) )

                for d_lst in orbit_lst:

                    # check whether involution inv.M preserves d_lst
                    dm_lst = [ d.mat_mul( inv.M ) for d in d_lst ]
                    dm_lst.sort()
                    if dm_lst != d_lst:
                        continue

                    # add to classification if not equivalent to objects
                    # in list, see "DPLattice.__eq__()".
                    dpl = DPLattice( d_lst, inv.Md_lst, inv.M )
                    if dpl not in dpl_lst:
                        dpl.set_attributes()
                        dpl_lst += [dpl]

        # store in cache
        dpl_lst.sort()
        NSTools.get_tool_dct()[key] = dpl_lst
        NSTools.save_tool_dct()

        return dpl_lst


    @staticmethod
    def get_part_roots( inv ):
        '''
        Return two subsets of roots using the input involution.
        
        This method is used by get_cls().        
                    
        Parameters
        ----------
        inv : DPLattice
            We expect inv.type=='A0'.
            We will use inv.Mtype and inv.M. 
        
        Returns
        -------
        list<Div>, list<Div>
            Let R be defined by the list
                get_divs( get_ak( inv.get_rank() ), 0, -2, True )
            whose elements are Div objects.
            If r is a Div object, then M(r) is shorthand notation for 
                r.mat_mul(inv.M)
            and r>0 means
                r.is_positive()
            The two returned lists correspond respectively to                       
                S := { r in R | M(r)=r }            
            and
                Q union Q' := { r in R | M(r) not in {r,-r} and r*M(r)>0 and r>0 and M(r)>0 }
            where Q = M(Q').                        
        '''
        r_lst = get_divs( get_ak( inv.get_rank() ), 0, -2, True )
        s_lst = [ r for r in r_lst if r.mat_mul( inv.M ) == r ]
        tq_lst = [ r for r in r_lst if r.mat_mul( inv.M ) not in [r, r.int_mul( -1 )] ]
        tq_lst = [ q for q in tq_lst if q * q.mat_mul( inv.M ) >= 0 and q.is_positive() and q.mat_mul( inv.M ).is_positive() ]

        q_lst = []
        for q in sorted( tq_lst ):
            if q not in q_lst and q.mat_mul( inv.M ) not in q_lst:
                q_lst += [q]

        NSTools.p( 'r_lst      =', r_lst )
        NSTools.p( 's_lst      =', s_lst )
        NSTools.p( 'q_lst      =', q_lst )
        NSTools.p( '       M -->', [q.mat_mul( inv.M ) for q in q_lst] )
        NSTools.p( 'inv.Md_lst =', inv.Md_lst )

        return s_lst, q_lst


    @staticmethod
    def get_num_types( inv, dpl, bas_lst ):
        '''
        Computes the maximal number of root basis in the 
        eigenspace of eigenvalue 1 of the involution defined by M.inv.   

        For example, if rank==6 and inv.Mtype=='A1' and dpl.type=='2A1',
        then there exists exactly one DPLattice bas in bas_lst such that bas.type=='3A1'        
        and such that d_lst is 
            [e1-e2, e0-e1-e2-e5, e0-e3-e4-e5] 
        or equivalently
            [e1-e2, e0-e4-e5, e0-e1-e2-e3].
        However the following two bases of type 2A1
            [e0-e1-e2-e5, e0-e3-e4-e5] and [e0-e4-e5, e0-e1-e2-e3]
        are inequivalent and e1-e2 (the eigenvector of (-1)) is orthogonal to both of them.
        In this case we return 2.
                 
        For example, if rank==6 and inv.Mtype=='A1' and dpl.type=='A1',
        then there exist exactly two DPLattices in bas_lst with type=='2A1'.
        In this case we return 2.

        This method is used by get_cls().
        
        Parameters
        ----------
        inv : DPLattice
        
        dpl : DPLattice
        
        bas_lst : list<DPLattice>
            We expect this to be the output of get_bas_lst()
            Thus a list of inequivalent DPLattice objects
         
        Returns
        -------
        int
            If there does not exists a DPLattice in bas_lst whose type is 
            inv.Mtype and bas.type combined, then return 0. 
            Otherwise return the number of DPLattices in bas_lst 
            with the same type as bas.type. We expect this number 
            to be either 1 or 2.                  
        '''
        num = 0  # number of root subsystems with fixed Dynkin type
        a_lst = convert_type( inv.Mtype )
        b_lst = convert_type( dpl.type )
        dpl_lst = []
        for bas in bas_lst:
            if sorted( a_lst + b_lst ) == convert_type( bas.type ):
                num += 1
            if bas.type == dpl.type:
                dpl_lst += [dpl]
        if num == 0:
            return 0
        else:
            return max( len( dpl_lst ), num )


    @staticmethod
    def is_inv_basis( d_lst, dtype ):
        '''
        This method is used by get_cls().
                
        Parameters:
        -----------
        d_lst: list<Div>
            List of divisors representing a root bases.
            
        dtype: string
            The Dynkin type of the root bases represented by d_lst.
                        
        Returns
        -------
        bool
            True iff there exists a basis of Dynkin type "dtype" that is invariant 
            under an involution such that this basis does not have  
            elements that are fixed by this involution.
            
        Notes
        -----
        For example '3A2+2A1' is a candidate, but 'A3+A2' and 'A1+A3' are not.
        
        '''
        if 'E' in dtype:
            return False

        if 'D' in dtype:
            return False

        if len( d_lst ) % 2 != 0:
            return False

        tp_lst = convert_type( dtype )

        # create the list on_lst of odd integers n such that An is contained in type
        on_lst = [ tp[1:] for tp in tp_lst if int( tp[1:] ) % 2 != 0 ]
        for on in on_lst:

            # if n is odd, then An must occur in pairs
            if tp_lst.count( 'A' + on ) % 2 != 0:
                return False

        return True


    @staticmethod
    def seek_bases( inv, d_lst, r_lst, num = -1, b_lst = [], bas_lst = [] ):
        '''
        This method is used by get_cls().
        
        Parameters
        ----------
        inv : DPLattice
            We use inv.Md_lst and inv.M.
        
        d_lst : list<Div>
            We use the intersection matrix associated to d_lst. 
        
        r_lst : list<Div>     
            A list of roots in which we look for bases.
        
        num : int
            If not -1 we stop after we found num different bases.
            If -1, then we assume that b.mat_mul(inv.M) not in b_lst
            for all b in b_lst.
        
        b_lst : list<Div>
            Used for recursive calling this method and 
            represents (a subset of) a candidate root bases.
        
        bas_lst : list<DPLattice>
            Used for recursive calling this method and
            is the list of inequivalent DPLattice objects that
            is returned by this method. 
            
        Returns 
        -------
        list<DPLattice>
            A list of DPLattice objects "bas"
            such that bas.type is equal to the Dynkin type of d_lst            
            and bas.Mtype==inv.Mtype and bas.M==inv.M.
            If num!=-1, then the lattice objects are inequivalent
            and the Dynkin type is instead two times the type of d_lst.        
        '''

        # check whether the constructed bases defines new DPLattice objects
        if len( b_lst ) == len( d_lst ):

            # make b_lst is invariant under the involution
            if num == -1:
                b_lst += [b.mat_mul( inv.M ) for b in b_lst]

            # create a new basis
            bas = DPLattice( b_lst, inv.Md_lst, inv.M )

            # check whether there is an equivalent object in bas_lst
            if num != -1 and bas in bas_lst:
                return bas_lst

            # return bas_lst appended with the new DPLattice object
            return bas_lst + [bas]

        # go through all possible roots to build up a basis like d_lst
        s = d_lst[ len( b_lst ) ]
        m_lst = [ d * s for d in d_lst  ][:len( b_lst )]
        for r in r_lst:

            # check intersection properties
            if [b * r for b in b_lst] == m_lst:

                # recursive call
                bas_lst = DPLattice.seek_bases( inv, d_lst, r_lst, num, b_lst + [r], bas_lst )

                # break out of for loop if we found enough DPLattice objects
                if len( bas_lst ) == num:
                    break

        return bas_lst


    @staticmethod
    def get_cls( rank = 9 ):
        '''
        Parameters
        ----------
        max_rank : int
            An integer in [3,...,9].           
    
        Returns
        -------
        list<DPLattice>
            A list of DPLattice objects corresponding to Neron-Severi lattices 
            of weak Del Pezzo surfaces of degree (10-rank). The list contains
            exactly one representative for each equivalence class.
              
            All the Div objects referenced in the DPLattice objects of 
            the output have the default intersection matrix:
                diagonal matrix with diagonal: (1,-1,...,-1). 
        '''
        # check cache
        key = 'get_cls__' + str( rank )
        # TODO TODO TODO remove FALSE!
        if False:
            if key in NSTools.get_tool_dct():
                return NSTools.get_tool_dct()[key]

        # determine possible root bases and involutions
        #
        inv_lst = DPLattice.get_inv_lst( rank )
        bas_lst = DPLattice.get_bas_lst( rank )
        NSTools.p( 'inv_lst =', [inv.get_marked_Mtype() for inv in inv_lst] )
        NSTools.p( 'bas_lst =', [bas.type for bas in bas_lst] )


        # we initialize the output list with DPLattice objects such that Mtype is 'A0'
        #
        dpl_lst = [ bas for bas in bas_lst ]


        # we loop through all involutions
        #
        eta = ETA( ( len( inv_lst ) - 1 ) * len( bas_lst ), 1 )
        for inv in inv_lst:
            if inv.Mtype == 'A0':
                continue

            # Construct the list dp1_lst of root bases that are contained in s_lst.
            #
            s_lst, q_lst = DPLattice.get_part_roots( inv )
            dpls_lst = [inv]  # list of DPLattice objects for s_lst
            dplq_lst = [inv]  # list of DPLattice objects for q_lst
            for bas in bas_lst:
                eta.update( inv.get_marked_Mtype() + ',' + bas.type )

                if bas.type == 'A0':
                    continue

                # construct bases of type bas.type in s_lst
                num = DPLattice.get_num_types( inv, bas, bas_lst )
                if num > 0:
                    tmp_lst = DPLattice.seek_bases( inv, bas.d_lst, s_lst, num )
                    for tmp in tmp_lst:
                        if tmp not in dpls_lst:
                            dpls_lst += [tmp]

                # construct bases of type bas.type in q_lst
                # if DPLattice.is_inv_basis( bas.d_lst, bas.type ):
                dplq_lst += DPLattice.seek_bases( inv, bas.d_lst, q_lst )


            # construct a list of combinations of DPLattice objects in
            # dpls_lst and dplq_lst
            #
            for dpls in dpls_lst:
                for dplq in dplq_lst:
                    d_lst = dpls.d_lst + dplq.d_lst  # notice that d_lst can be equal to []
                    if is_root_basis( d_lst ):
                        dpls.set_attributes( 8 )
                        dplq.set_attributes( 8 )
                        NSTools.p( inv.get_marked_Mtype() + ', ' + dpls.type + '[+]' + dplq.type,
                                   '; dpls.d_lst =', dpls.d_lst,
                                   ', dplq.d_lst =', dplq.d_lst,
                                   ', s_lst =', s_lst,
                                   ', q_lst =', q_lst,
                                   ', inv.Md_lst =', inv.Md_lst )
                        dpl = DPLattice( d_lst, inv.Md_lst, inv.M )
                        if dpl not in dpl_lst:
                            dpl.set_attributes()
                            dpl_lst += [dpl]

        # store in cache
        dpl_lst.sort()
        NSTools.get_tool_dct()[key] = dpl_lst
        NSTools.save_tool_dct()

        return dpl_lst


    # overloading of "=="
    # returns True if isomorphic as Neron-Severi lattices
    def __eq__( self, other ):

        # compared with None?
        if type( self ) != type( other ):
            return False

        # cardinality of classes agree?
        if len( self.d_lst ) != len( other.d_lst ):
            return False
        self.set_attributes( 0 )
        other.set_attributes( 0 )
        if len( self.m1_lst ) != len( other.m1_lst ):
            return False
        self.set_attributes( 1 )
        other.set_attributes( 1 )
        if len( self.fam_lst ) != len( other.fam_lst ):
            return False
        self.set_attributes( 2 )
        other.set_attributes( 2 )
        if len( self.real_d_lst ) != len( other.real_d_lst ):
            return False
        self.set_attributes( 3 )
        other.set_attributes( 3 )
        if len( self.real_m1_lst ) != len( other.real_m1_lst ):
            return False
        self.set_attributes( 4 )
        other.set_attributes( 4 )
        if len( self.real_fam_lst ) != len( other.real_fam_lst ):
            return False
        self.set_attributes( 5 )
        other.set_attributes( 5 )
        if len( self.or_lst ) != len( other.or_lst ):
            return False
        self.set_attributes( 6 )
        other.set_attributes( 6 )
        if len( self.sr_lst ) != len( other.sr_lst ):
            return False

        # Dynkin type effective (-2)-classes agree?
        self.set_attributes( 7 )
        other.set_attributes( 7 )
        if self.type != other.type:
            return False

        # Mtype may differ for equivalent DPLattice objects

        # check Cremona invariant
        self.set_attributes( 9 )
        other.set_attributes( 9 )
        if not self.G.is_isomorphic( other.G, edge_labels = True ):
            return False

        return True


    # operator overloading for <
    # Used for sorting lists of DPLattice objects:
    #     <http://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes-in-python>
    def __lt__( self, other ):

        if self.get_rank() != other.get_rank():
           return self.get_rank() < other.get_rank()

        if len( self.Md_lst ) != len( other.Md_lst ):
           return len( self.Md_lst ) < len( other.Md_lst )

        self.set_attributes( 8 )
        other.set_attributes( 8 )

        if self.Mtype != other.Mtype:
            return self.type < other.type

        if self.get_marked_Mtype() != other.get_marked_Mtype():
            return self.get_marked_Mtype() < other.get_marked_Mtype()

        if len( self.d_lst ) != len( other.d_lst ):
            return len( self.d_lst ) < len( other.d_lst )

        if self.type != other.type:
            return self.type < other.type

        if len( self.real_fam_lst ) != len( other.real_fam_lst ):
            return len( self.real_fam_lst ) > len( other.real_fam_lst )

        if len( self.fam_lst ) != len( other.fam_lst ):
            return len( self.fam_lst ) < len( other.fam_lst )

        if len( self.m1_lst ) != len( other.m1_lst ):
            return len( self.m1_lst ) < len( other.m1_lst )


    # overloading of "str()": human readable string representation of object
    def __str__( self ):

        self.set_attributes()

        s = '\n'
        s += 50 * '=' + '\n'

        s += 'Degree          = ' + str( self.get_degree() ) + '\n'
        s += 'Rank            = ' + str( self.get_rank() ) + '\n'
        s += 'Intersection    = ' + str( list( self.m1_lst[0].int_mat ) ) + '\n'
        s += 'Real structure  = ' + str( self.get_marked_Mtype() ) + '\n'
        s += 'Singularities   = ' + str( self.type ) + '\n'
        s += 'Cardinalities   = ' + '(' + str( len( self.or_lst ) ) + ', ' + str( len( self.sr_lst ) ) + ')\n'

        arrow = '  --->  '

        s += 'Real involution:\n'
        b_lst = [Div( row ) for row in sage_identity_matrix( sage_ZZ, self.get_rank() ).rows() ]
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


