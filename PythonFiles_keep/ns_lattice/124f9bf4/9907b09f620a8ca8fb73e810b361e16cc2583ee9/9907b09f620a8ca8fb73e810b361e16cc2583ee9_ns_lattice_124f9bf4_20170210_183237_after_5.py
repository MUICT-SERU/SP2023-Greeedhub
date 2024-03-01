'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 9, 2017
@author: Niels Lubbes
'''

from ns_lattice import *
nt = NSTools()



def get_base_changes( rank, d_lst = [], div_dct = None ):
    '''
    Computes a basis change for a NS-lattice of a Del Pezzo surface.
    In order to obtain such a basis, we subsequently contract 
    (-1)-curves until we arrive either at P^1xP^1 or at P^2.
    
    INPUT:         
        - "rank"    --  An integer between 3 and 9.

        - "d_lst"   --  A list of "Div" objects of the same rank==r+1
                        such that 
                            (3h-e1-...-er)*d==0 and d^2==-2
                        for all d in "d_lst". Thus such divisors 
                        represent effective (-2)-classes.
                        The intersection matrix of the Div objects
                        is assumed to be the default: a diagonal
                        matrix with diagonal (1,-1,...,-1). 

        - "div_dct" --  A dictionary representing the current NS-lattice 
                        and either has the following entries:
         
                            * div_dct['ray_lst']: 
                              List of Div objects of (-1) classes that
                              were contracted. First in list in contracted
                              last.

                            * div_dct['k']: 
                              The canonical divisor class.

                            * div_dct['fam_lst']:
                              List of Div objects f such that 
                               (3h-e1-...-3r)*f==2 and f^2==0
                              for all f in the list.
                              See also "div_set.get_fam_classes()"
                            
                            * div_dct['m1_lst']: 
                              List of Div objects corresponding 
                              to (-1)-classes that can be contracted.
                              See also "div_set.get_m1_classes()"
                                                                                  
                        For initial call the default is None,
                        and used for recursive calls of this method.                              
    
    OUTPUT:
        - Returns a list rank*rank matrices over ZZ, such that the 
          rows of the matrix represent generators for a new basis.
                    
          There are two types of matrices in this list:

            (I) The first row has self-intersection one
                and the remaining rows have self-intersection 
                minus one. This basis corresponds to a basis 
                of the Neron-Severi lattice of the projective 
                plane P^2 blown up in points: <h,e1,...,er> 
                such h^2==1 and e1**2==-1,...er**2==-1,
                and the remaining intersections are zero.
                Thus the diagonal matrix corresponding to 
                this bilinear intersection product has 
                diagonal (1,-1,...,-1).
                                                                              
           (II) The first two of the matrix have self- 
                intersection zero and the remaining rows
                have self-intersection minus one.
                This basis corresponds to a basis of 
                the Neron-Severi lattice of P^1xP^1
                blown up in points: <h,e1,...,er>
                such that h*e1==1, e2**2==-1,...er**2==-1, 
                and the remaining intersections are zero.      
                Thus the matrix corresponding to this
                bilinear intersection product is
                the identity matrix with the first two 
                columns switched.  
                                      
    '''
    # initialize div_dct
    if div_dct == None:
        div_dct = {}
        div_dct['ray_lst'] = []
        div_dct['k'] = Div( [-3] + ( rank - 1 ) * [1] )  # k = -3h+e1+...+er
        div_dct['fam_lst'] = get_fam_classes( rank, True, d_lst )
        div_dct['m1_lst'] = get_m1_classes( rank, True, d_lst )

        for d in d_lst:
            if d.rank() != rank:
                raise ValueError( 'All Div objects in d_lst argument must have rank:', rank )

    # output info
    if True:
        nt.p( 10 * '-' )
        for key in ['ray_lst', 'k', 'fam_lst', 'm1_lst']:
            nt.p( key, '=', div_dct[key] )
        nt.p( 'd_lst =', d_lst )

    # are
    if div_dct['m1_lst'] == []:

        gen_lst = []

        if len( div_dct['fam_lst'] ) == 0:

            # P^2
            ck_lst = div_dct['k'].e_lst  # k=-3h
            h = Div( [-ck / 3 for ck in ck_lst ] )
            gen_lst = [h] + div_dct['ray_lst']

        elif len( div_dct['fam_lst'] ) == 2:

            # P^1xP^1
            gen_lst = div_dct['fam_lst'] + div_dct['ray_lst']

        else:
            # fiber bundle
            return []

        mat = matrix( ZZ, [ gen.e_lst for gen in gen_lst ] )  # rows form new basis
        return [mat]

    else:
        # contract ray and call method recursively

        mat_lst = []
        for ray in div_dct['m1_lst']:

            new_dct = {}
            new_dct['ray_lst'] = [ray] + div_dct['ray_lst']
            new_dct['k'] = div_dct['k'] - ray
            new_dct['fam_lst'] = [ fam for fam in div_dct['fam_lst'] if fam * ray == 0 ]
            new_d_lst = [ d for d in d_lst if d * ray == 0]


            # add (-1)-curves that appeared previously as (-2)-curve
            new_dct['m1_lst'] = [ a for a in div_dct['m1_lst'] if a * ray == 0]
            new_dct['m1_lst'] += [d + ray.int_mul( d * ray ) for d in d_lst if d * ray > 0]
            for m1 in new_dct['m1_lst']:
                if m1 * m1 != -1 or m1 * new_dct['k'] != -1 or m1 * ray != 0:
                    raise Exception( 'Expect only (-1)-curves orthogonal to ray.' )


            mat_lst += get_base_changes( rank, new_d_lst, new_dct )

        return mat_lst


def get_real_base_changes( dpl ):
    '''
    INPUT:
        - "dp_lat"  -- DPLattice object.
    OUTPUT
        - "mat_lst" -- A list of matrices corresponding to base changes of
                       the Neron-Severi lattice, which are compatible 
                       with the real structure in the following way.
                       
                       First we consider the output of ".get_base_changes()"
                       which is a list of matrices of type (I) and (II).
                       
                       If the matrix is of type (I) with basis: 
                           <h,e1,...,er>
                       then we include the matrix in the output list of 
                       this method, if the involution sends h to h
                       and preserves the set {e1,..,er}. 
                                              
                       If the matrix is of type (II) with basis: 
                           <h,e1,...,er>
                       then we include the matrix in the output list of 
                       this method, if the involution sends h to h,
                       e1 to e1 and preserves the set {e2,..,er}.                                                
        
        - "dpl_lst" -- A list of "DPLattice" objects such that 
                       each lattice represents the same lattice 
                       as the input "dp_lat", but wrt. a different basis
                       coming from a matrix in "mat_lst". 
    '''
    dpl_lst = []
    for mat in get_base_changes( dp_lat.get_rank(), dp_lat.d_lst ):

        B = mat.T  # columns form generators for bases

        dpl = DPLattice()
        dpl.M = ~B * dp_lat.M * B  # new matrix for involution
        dpl.Md_lst = [ Md.mat_mul( B ) ]




if __name__ == '__main__':

    # mat_lst = get_base_changes( 3, [Div( [0, 1, -1] )] )
    # mat_lst = get_base_changes( 4, [Div( [0, 1, -1, 0] )] )
    mat_lst = get_base_changes( 5, [] )


    for mat in mat_lst:
        print list( mat )
        # print '\t\tchk_lst += [', list( mat ), ']'

    print
    print 'The End'
