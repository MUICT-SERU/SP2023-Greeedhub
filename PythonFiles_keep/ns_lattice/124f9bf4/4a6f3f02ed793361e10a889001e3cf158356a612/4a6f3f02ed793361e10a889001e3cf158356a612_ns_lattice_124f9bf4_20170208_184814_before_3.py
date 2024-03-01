'''
Created on Aug 11, 2016
@author: Niels Lubbes
'''
from sage.all import *

from ns_tools import *

class Div:
    '''
    The class represents an element in the Neron-Severi group.
    Thus a divisor class up to numerical equivalence.
    
    In the documentation of this class we denote the standard basis
    as:
        <h,e1,e2,...>
    '''

    # static variable
    short_output = True

    def __init__( self, e_lst = 9 * [0], signature_mat = None ):
        '''
        INPUT:
            - "e_lst "        -- A list of elements in ZZ.
            - "signature_mat" -- A matrix over ZZ of rank "len(e_lst)".                                 
        OUTPUT:
            - Constructor.
              If "signature_mat==None" then the default 
              diagonal matrix has signature (+-...-). 
        '''

        self.e_lst = list( e_lst )

        if signature_mat != None:
            self.signature_mat = signature_mat
        else:
            self.signature_mat = diagonal_matrix( ZZ, [1] + ( self.rank() - 1 ) * [-1] )

    def rank( self ):
        return len( self.e_lst )

    @staticmethod
    def get_min_rank( lbl ):
        '''
        INPUT:
            - "lbl"  -- A string with format as output of "self.get_label()".
        OUTPUT:
            - The minimal rank of the "Div" object with a given label.
        
        EXAMPLE:
            - "get_rank('78')    == 9  "
            - "get_rank('301')   == 9  "
            - "get_rank('12')    == 3  "
        '''
        d = Div.new( lbl )
        lst = copy( d.e_lst )
        while lst[-1] == 0 and lst != []:
            lst.pop()

        return len( lst )


    @staticmethod
    def new( lbl, rank = 9 ):
        '''
        INPUT:
            - "lbl"  -- A string with format as output of "self.get_label()".
            - "rank" -- Integer representing rank of Neron-Severi lattice
                        in which "Div" lives.
        OUTPUT:
            - The "Div" corresponding to the label 
              such that "len(self.e_lst)>=rank".
        '''

        c = Div( rank * [0] )  # zero divisor class

        if 'e' in lbl or 'h' in lbl:

            if 'h' in lbl:
                c.e_lst = [ int( lbl.split( 'h' )[0] ) ]  # [4] if lbl='4h+3e...'
                s = lbl.split( 'h' )[1]  # for example '+3e2-2e5+6e7+e8'
            else:
                c.e_lst = [0]
                s = lbl

            coef_e = ''
            idx = 0
            last_i = 0  # ei
            while idx < len( s ):
                if s[idx] != 'e':
                    coef_e += s[idx]
                    idx += 1
                elif s[idx] == 'e':
                    coef_i = ''
                    idx += 1
                    while idx < len( s ) and s[idx] not in ['+', '-']:
                        coef_i += s[idx]
                        idx += 1
                    i = int( coef_i )
                    if coef_e == '-': coef_e = '-1'
                    if coef_e in ['+', '']: coef_e = '1'
                    c.e_lst += ( i - last_i - 1 ) * [0] + [int( coef_e )]
                    coef_e = ''
                    last_i = i

        else:  # label of (-2)-class

            if rank > 9:
                raise ValueError( 'For (-2)-classes we expect the rank to be at most 9: ', rank )

            # check whether the label is negative
            if lbl[0] == '-':
                neg = True
                lbl = lbl[1:]
            else:
                neg = False

            # '12' ---> e1-e2
            if len( lbl ) == 2:
                c.e_lst[ int( lbl[0] ) ] = 1
                c.e_lst[ int( lbl[1] ) ] = -1

            # '1123' ---> h-e1-e2-e3
            elif len( lbl ) == 4 and lbl[0] == '1':
                c.e_lst[0] = int( lbl[0] )
                c.e_lst[ int( lbl[1] ) ] = -1
                c.e_lst[ int( lbl[2] ) ] = -1
                c.e_lst[ int( lbl[3] ) ] = -1

            # '212' ---> 2h-e3-e4-...-e8
            elif len( lbl ) == 3 and lbl[0] == '2':
                c.e_lst = 9 * [-1]
                c.e_lst[0] = int( lbl[0] )
                c.e_lst[ int( lbl[1] ) ] = 0
                c.e_lst[ int( lbl[2] ) ] = 0
                if rank != 9 and set( c.e_lst[rank:] ) != set( [0] ):
                    raise ValueError( 'Rank too low for label: ', rank, lbl )
                c.e_lst = c.e_lst[:rank]

            # '308' ---> 3h-e1-e2-...-e7-2e8
            elif len( lbl ) == 3 and lbl[0] == '3' and lbl[1] == '0':
                c.e_lst = 9 * [-1]
                c.e_lst[0] = int( lbl[0] )
                c.e_lst[ int( lbl[2] ) ] = -2

            else:  # unknown label
                raise ValueError( 'Label has incorrect format: ', lbl )

            # for example '-12'=[0,-1,1,0,0,...]
            if neg:
                c.e_lst = [ -e for e in c.e_lst ]


        # end handling label of (-2)-class


        # update rank
        c.e_lst = c.e_lst + ( rank - len( c.e_lst ) ) * [0]

        return c

    def __get_minus_two_label( self ):
        '''
        Private helper method for "get_label()"
        INPUT:
            - "self" -- self*self==-2 and self.rank<=9.
        OUTPUT: 
            - See output documents for self.get_label()
        '''

        if self * self != -2 or self.rank() > 9:
            raise ValueError( 'Unexpected input for __get_mt_label: ', self.e_lst )

        # first non-zero coefficient negative?
        neg = [e < 0 for e in self.e_lst if e != 0][0]

        # check whether the label should start with minus symbol
        if neg:
            tmp = [-e for e in self.e_lst]
        else:
            tmp = self.e_lst

        # set of non-zero coefficients for ei.
        oset = set( [ e for e in tmp[1:] if e != 0 ] )

        # e1-e2 ---> '12'
        if tmp[0] == 0 and oset == set( [1, -1] ):
            lbl = ''
            for i in range( 1, len( tmp ) ):
                if tmp[i] != 0:
                    lbl += str( i )

        # h-e1-e2-e3 ---> '1123'
        elif tmp[0] == 1 and oset == set( 3 * [-1] ):
            lbl = '1'
            for i in range( 1, len( tmp ) ):
                if tmp[i] != 0:
                    lbl += str( i )

        # 2h-e3-e4-...-e8 ---> '212'
        elif tmp[0] == 2 and oset == set( 6 * [-1 ] ):
            lbl = '2'
            for i in range( 1, len( tmp ) ):
                if tmp[i] == 0:
                    lbl += str( i )

        # 3h-e1-e2-...-e7-2e8 ---> '308'
        elif tmp[0] == 3 and oset == set( 7 * [-1 ] + [-2] ):
            lbl = '30'
            for i in range( 1, len( tmp ) ):
                if tmp[i] == -2:
                    lbl += str( i )

        if neg:
            lbl = '-' + lbl  # for example: 12 --> -12

        return lbl


    def get_label( self, abbr = False ):
        '''
        INPUT:
            - "abbr" -- A Boolean. 
        
        OUTPUT:
        
            - We describe the output label in terms of examples.
            
            * If "abbr==True":
              
                > e1                --->  'e1'
                > e1-e2             --->  'e12'  
                > h-e1              --->  '1e1'
                > 2h-e1-e2-e4-e5    --->  '2e1245'  
        
            * If "abbr==False" and self*self==-2 and self.rank()<=9:
            
                >  e1-e2               ---> '12'
                > -e1+e2               ---> '-12'
                >   h-e1-e2-e3         ---> '1123'
                >  2h-e3-e4-...-e8     ---> '212'
                >  3h-e1-e2-...-e7-2e8 ---> '308'
                > -3h+e1+e2+...+e7+2e8 ---> '-308'  
                
            * For the remaining cases not treated above:
            
                > 3h-2e1-13e2-4e3  ---> '3h-2e1-13e2-4e3'                                
            
            
        '''

        divK = Div( [-3] + ( self.rank() - 1 ) * [1] )

        if abbr:

            np1 = len( [e for e in self.e_lst[1:] if e == 1] )
            nm1 = len( [e for e in self.e_lst[1:] if e == -1] )
            n01 = len( [e for e in self.e_lst[1:] if e > 1 or e < -1] )

            if n01 == 0 and self[0] in range( 0, 10 ):

                # e1
                if self[0] == 0 and np1 == 1 and nm1 == 0:
                    return 'e' + str( self.e_lst.index( 1 ) )

                # e1-e2
                if self[0] == 0 and np1 == 1 and nm1 == 1:
                    return 'e' + str( self.e_lst.index( 1 ) ) + str( self.e_lst.index( -1 ) )

                # 2h-e1-e2-e3-e4-e5 or h-e1
                if self[0] in range( 0, 10 ) and np1 == 0 and nm1 > 0:
                    lbl = str( self[0] ) + 'e'
                    for i in range( 1, len( self.e_lst ) ):
                        if self[i] != 0:
                            lbl += str( i )
                    return lbl

        elif self * self == -2 and self.rank() <= 9 and self * divK == 0:
            return self.__get_minus_two_label()


        # from this point on we treat the general case
        #
        lbl = ''
        for i in range( 0, len( self.e_lst ) ):
            val = self[i]
            if val != 0:

                if val == 1:
                    if lbl != '': lbl += '+'
                elif val == -1:
                    lbl += '-'
                else:
                    if val > 1 and lbl != '':
                        lbl += '+'
                    lbl += str( val )

                if i == 0:
                    lbl += 'h'
                else:
                    lbl += 'e' + str( i )

        return lbl


    def mat_mul( self, M ):
        '''
        INPUT:
            - "self" -- A "Div" object.
            - "M"    -- A matrix with self.rank() columns.
        OUTPUT:
            - Returns a "Div" object that is a result of 
              applying the linear transformation corresponding
              to "M" to itself. 
        '''
        v = vector( self.e_lst ).column()
        return Div( ( M * v ).list() )


    def int_mul( self, n ):
        '''
        INPUT:
            - "self" -- A "Div" object.
            - "n"    -- An integer.
        OUTPUT:
            - Returns a "Div" object that is a result of 
              multiplying with the scalar "n". 
        '''
        return self.mat_mul( diagonal_matrix( self.rank() * [n] ) )


    # operator overloading for ==
    def __eq__( self, other ):
        return self.e_lst == other.e_lst

    # operator overloading for !=
    def __ne__( self, other ):
        return not self.__eq__( other )

    # operator overloading for <
    # Used for sorting lists of "Div"-objects:
    #     <http://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes-in-python>
    def __lt__( self, other ):

        if self.rank() != other.rank():
           return self.rank() < other.rank()

        a = self.e_lst
        b = other.e_lst

        if a[0] != 0 and b[0] != 0:
            if a[0] != b[0]:
                return a[0] < b[0]  # example: 1123 < 308
            else:
                return a[1:] > b[1:]  # example: 1124 < 1123

        if ( a[0], b[0] ) != ( 0, 0 ):
            return a[0] < b[0]  # example: 12 < 1123

        # a[0]==b[0]==0

        if a.index( 1 ) == b.index( 1 ):
            return a > b  # example 13 < 12

        return a < b  # example: 34 < 12


    # operator overloading for *
    def __mul__( self, div ):
        '''
        INPUT:
            - "div" -- A "Div" object.
        OUTPUT:
            - The intersection product of "self" and 
              "div" wrt. to signature "self.signature_mat".
        '''

        row_vec = vector( ZZ, self.e_lst ).row()
        col_vec = vector( ZZ, div.e_lst ).column()
        mat = self.signature_mat

        v = row_vec * mat * col_vec

        return v[0][0]

    # operator overload for +
    def __add__( self, div ):
        v = vector( ZZ, self.e_lst ) + vector( ZZ, div.e_lst )
        return Div( list( v ) )

    # operator overloading for []
    def __getitem__( self, index ):
        return self.e_lst[index]

    # operator overloading for []
    def __setitem__( self, index, item ):
        self.e_lst[index] = item

    # overloading for str(.): human readable string representation of object
    def __str__( self ):
        if Div.short_output:
            return self.get_label()
        else:
            return str( self.e_lst )

    # overloading "repr" as well, since python call this for Div objects in a list
    def __repr__( self ):
        return self.__str__()
