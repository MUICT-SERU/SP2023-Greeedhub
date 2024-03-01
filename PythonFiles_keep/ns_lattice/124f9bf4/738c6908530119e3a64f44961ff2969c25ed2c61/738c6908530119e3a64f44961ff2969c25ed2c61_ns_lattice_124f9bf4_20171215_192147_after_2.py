'''
Created on Aug 15, 2016
@author: Niels Lubbes

This module is for classifying real structures and singularities 
of weak Del Pezzo surfaces of degree between 1 and 7.

'''
import time

from sage_interface import sage_identity_matrix
from sage_interface import sage_ZZ
from sage_interface import sage_QQ
from sage_interface import sage_Subsets
from sage_interface import sage_VectorSpace
from sage_interface import sage_vector

from div_in_lattice import get_divs
from div_in_lattice import get_indecomp_divs
from div_in_lattice import get_ak

from dp_root_bases import get_ext_graph
from dp_root_bases import get_dynkin_type
from dp_root_bases import get_root_bases_orbit
from dp_root_bases import is_root_basis

from dp_involutions import basis_to_involution
from dp_involutions import is_integral_involution

from class_ns_tools import NSTools

from class_div import Div


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
        Geometrically these classes correspond to a real families of conics        
   
    self.or_lst : list<Div>
        A list of "Div" objects that represents roots that are orthogonal to
        "self.d_lst".  

    self.sr_lst : list<Div>
        A list of "Div" objects that represents roots that are contained in
        the subspace spanned by "self.d_lst".  
    
    self.G : sage_Graph
        The Cremona invariant for the current lattice.
    '''

    # Static variable. If False, then equivalent real structures with
    # different Dynkin types are considered equivalent. Equivalent real
    # structures can have several Dynkin types. We set this variable to
    # False in order to register this. See also get_reduced_cls()
    weak_equality = False

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
            A positive number.
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
    def get_cls_root_bases( rank = 9 ):
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
        # classification of root bases in cache?
        key = 'get_cls_root_bases_' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        A = [ 12, 23, 34, 45, 56, 67, 78]
        B = [ 1123, 1145, 1456, 1567, 1678, 278 ]
        C = [ 1127, 1347, 1567, 234, 278, 308 ]
        D = [ 1123, 1345, 1156, 1258, 1367, 1247, 1468, 1178 ]

        dpl_lst = []
        for ( lst1, lst2 ) in [ ( A, [] ), ( A, B ), ( A, C ), ( [], D ) ]:

            # restrict to divisors in list, that are of rank at most "max_rank"
            lst1 = [ Div.new( str( e ), rank ) for e in lst1 if rank >= Div.get_min_rank( str( e ) ) ]
            lst2 = [ Div.new( str( e ), rank ) for e in lst2 if rank >= Div.get_min_rank( str( e ) ) ]

            # data for ETA computation
            total = len( sage_Subsets( range( len( lst1 ) ) ) )
            total *= len( sage_Subsets( range( len( lst2 ) ) ) )
            counter = 0
            ival = 20

            NSTools.p( 'inside loop: ', lst1, lst2, ', rank = ', rank )

            # loop through the lists
            for idx2_lst in sage_Subsets( range( len( lst2 ) ) ):
                for idx1_lst in sage_Subsets( range( len( lst1 ) ) ):

                    # ETA
                    if counter % ival == 0:
                        start = time.time()
                    counter += 1
                    if counter % ival == 0:
                        passed_time = time.time() - start
                        NSTools.p( 'ETA in minutes =', passed_time * ( total - counter ) / ( ival * 60 ), idx1_lst, idx2_lst, ', rank =', rank )

                    # construct d_lst as a union
                    d_lst = []
                    d_lst += [ lst1[idx1] for idx1 in idx1_lst ]
                    d_lst += [ lst2[idx2] for idx2 in idx2_lst ]

                    if not is_root_basis( d_lst ):
                        continue

                    Md_lst = []
                    M = sage_identity_matrix( sage_QQ, rank )
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
    def get_cls_involutions( rank = 9 ):
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
        key = 'get_cls_invo_' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        bas_lst = DPLattice.get_cls_root_bases( rank )
        counter = 0
        total = len( bas_lst )
        inv_lst = []
        for bas in bas_lst:
            NSTools.p( 'counter =', counter , '/', total, ', root base = ', bas.d_lst )
            counter += 1
            M = basis_to_involution( bas.d_lst, rank )
            if not is_integral_involution( M ):
                continue
            inv = DPLattice( [], bas.d_lst, M )
            inv.set_attributes()
            inv_lst += [ inv ]

        # store in cache
        inv_lst.sort()
        NSTools.get_tool_dct()[key] = inv_lst
        NSTools.save_tool_dct()

        return inv_lst


    @staticmethod
    def get_cls_real_dp( rank = 7 ):
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
        key = 'get_cls_real_dp_' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        inv_lst = DPLattice.get_cls_involutions( rank )
        bas_lst = DPLattice.get_cls_root_bases( rank )


        # ETA
        ostart = time.time()
        ototal = len( bas_lst ) * len( inv_lst )
        ocounter = 0
        icounter = 0
        ival = 20
        total_orbit_len = 0


        # we fix an involution up to equivalence and go through
        # all possible root bases for singularities.
        dpl_lst = []
        for inv in inv_lst:
            for bas in bas_lst:

                orbit_lst = get_root_bases_orbit( bas.d_lst )

                # ETA outer loop
                ocounter += 1
                otime = ( time.time() - ostart ) / 60
                total_orbit_len += len( orbit_lst )
                avg_orbit_len = total_orbit_len / ocounter
                itotal = ( avg_orbit_len * ototal )
                NSTools.p( '#orbit =', len( orbit_lst ),
                           '(average =', avg_orbit_len, '),',
                           'ocounter =', ocounter, '/', ototal, ',',
                           'rank =', rank,
                           'total minutes passed =', otime,
                           'ETA in minutes =', ( otime / ocounter ) * ( ototal - ocounter ) )


                for d_lst in orbit_lst:

                    # ETA inner loop
                    if icounter % ival == 0:
                        istart = time.time()
                    icounter += 1
                    if icounter % ival == 0:
                        itime = ( time.time() - istart ) / 60
                        NSTools.p( 'ETA in minutes =', ( itime / ival ) * ( itotal - icounter ), ',',
                                   'icounter =', icounter, '/', itotal )

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
    def get_reduced_cls( max_rank = 9, invo_cls = False ):
        '''
        Parameters
        ----------
        max_rank : int
        invo_cls : bool
        
        Returns
        -------
        TODO
        '''
        # check cache
        key = 'get_reduced_cls' + str( max_rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        DPLattice.weak_equality = True
        dpl_dct = {}

        for rank in range( 3, max_rank + 1 ):

            dpl_lst = []

            if rank > 7:
                dpl_lst = DPLattice.get_cls_root_bases( rank ) + DPLattice.get_cls_involutions( rank )
            else:
                dpl_lst = DPLattice.get_cls_real_dp( rank )

            dpl_dct[rank] = []
            for dpl in dpl_lst:

                if dpl in dpl_dct[rank]:

                    for i in range( len( dpl_dct[rank] ) ):
                        if dpl_dct[rank][i] == dpl and dpl_dct[rank][i] < dpl:
                            dpl_dct[rank][i] = dpl

                else:

                    dpl_dct[rank] += [dpl]

        DPLattice.weak_equality = False

        # store in cache
        NSTools.get_tool_dct()[key] = TODO
        NSTools.save_tool_dct()

        return TODO


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

        # Dynkin type real structures agree?
        self.set_attributes( 8 )
        other.set_attributes( 8 )
        if not DPLattice.weak_equality:
            # In a finer classification, this check should be
            # omitted, since equivalent real structures may have
            # different Dynkin types.
            if self.Mtype != other.Mtype:
                return False

        # check Cremona invariant
        self.set_attributes( 9 )
        other.set_attributes( 9 )
        if not self.G.is_isomorphic( other.G, edge_labels = True ):
            NSTools.p( 'Non isomorphic graphs (unexpected position): ', self, other )
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

        if len( self.d_lst ) != len( other.d_lst ):
           return len( self.d_lst ) < len( other.d_lst )

        self.set_attributes( 8 )
        other.set_attributes( 8 )

        if self.Mtype != other.Mtype:
            return self.type < other.type

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
        s += 'Real structure  = ' + str( self.Mtype ) + '\n'
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


