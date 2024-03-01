'''
Created on Aug 11, 2016
@author: Niels Lubbes
'''
from sage.all import *

from class_ns_tools import NSTools
from class_div import Div

nt = NSTools()


def get_div_set( d, dc, cc, perm = False ):
    '''
    INPUT: 
        - "d"     -- "Div" object  d0*e0 + d1*e1 +...+ dr*er such that 
                        * product signature equals (1,d.rank()-1)
                        * d0>0
                        * d1,...,dr<=0                         
        - "dc"    -- A positive integer.
        - "cc"    -- An integer.        
        - "perm"  -- Boolean.  
              
    OUTPUT:
        - Returns a sorted list of "Div" objects
        
            * c = c0*e0 + c1*e1 +...+ cr*er
          
          such that 
                        
            * d.rank() == r+1
            * dc       == d*c   (signature = (1,rank-1))
            * cc       == c*c   (signature = (1,rank-1))           
            * c0 > 0
            * c1,...,cr <= 0               
    
          If "perm" is False then additionally: 
              
            * c1 <=... <= cr. 
           
    '''

    # check if input was already computed
    key = 'get_div_set_' + str( ( d, dc, cc, perm ) )
    if key in nt.get_tool_dct():
        return nt.get_tool_dct()[key]

    # construct div set
    nt.p( 'Constructing div set classes for ', ( d, dc, cc, perm ) )
    out_lst = []

    #
    # Cauchy-Schwarz inequality: <x,y>^2 <= <x,x>*<y,y>
    #
    # Note: cc = c0^2 - c1^2 -...- cr^2
    #
    c0 = 0
    while True:

        c0 = c0 + 1
        dc_tail = d[0] * c0 - dc  #    = d1*c1 +...+ dr*cr
        dd_tail = d[0] ** 2 - d * d  # = d1^2  +...+ dr^2
        cc_tail = c0 ** 2 - cc  #      = c1^2  +...+ cr^2

        # not possible according to io-specs.
        if dc_tail < 0:
            continue

        # Cauchy-Schwarz inequality holds?
        if dc_tail * dc_tail > dd_tail * cc_tail:
            break  # out of while loop

        nt.p( c0, dc_tail )

        # obtain all possible [d1*c1+1,...,dr*cr+1]
        r = d.rank() - 1
        if perm:
            p_lst_lst = Compositions( dc_tail + r, length = r )
        else:
            p_lst_lst = Partitions( dc_tail + r, length = r )

        # obtain [c1,...,cr] from [d1*c1+1,...,dr*cr+1]
        for p_lst in p_lst_lst:

            # dc_tail=d1*c1 +...+ dr*cr = p1 +...+ pr  with pi>=0
            p_lst = [ p - 1 for p in p_lst]

            # obtain c_tail=[c1,...,cr] from [p1,...,pr]
            valid_part = True
            c_tail = []  # =[c1,...,cr]
            for i in range( 0, len( p_lst ) ):
                nt.p( p_lst[i], d[i + 1] )
                if p_lst[i] == 0:
                    c_tail += [0]
                elif d[i + 1] == 0:
                    c_tail += [p_lst[i]]
                else:
                    quo, rem = ZZ( p_lst[i] ).quo_rem( d[i + 1] )
                    if rem != 0:
                        valid_part = False
                        break  # out of for-loop
                    else:
                        c_tail += [ quo ]
            if not valid_part:
                continue

            # add to out list if valid
            c = Div( [c0] + c_tail )
            if c.rank() == d.rank() and  dc == d * c and cc == c * c:
                out_lst += [c]

    # sort list of "Div" objects
    out_lst.sort()


    # cache output
    nt.get_tool_dct()[key] = out_lst
    nt.save_tool_dct()

    return out_lst


def get_m2_classes( rank, perm = False ):
    '''
    INPUT:
        - "rank" -- An integer between 2 and 9.
        - "perm" -- A boolean.
    OUTPUT:
        - Returns a sorted list of "Div" objects that 
          represent (-2)-classes on a 
          weak del Pezzo surface of rank (10-<rank>).

          We assume that the matrix of the intersection
          product of these divisors is a diagonal matrix
          with signature (-1,1,...,1).           
          
          Thus we return classes f such that 
              
              f*f==-2 and (-3e0+e1+...+er)*f==0
          
          with r=rank-1.
          The (positive) root classes are of the form either
          
            c0*e0-c1*e1-...-cr*er               
            
            or              
            
            ei-ej
          
          where the integers ci>0 and j>i.         
          
          The classes are '12', '1123', '212', '308'
          and if "perm=True" then also permutations of 
          the 'ei' coefficients (with the restriction that j>i).  
          See "Div.get_label()" for the notation.
                   
    '''
    if rank not in range( 2, 9 + 1 ):
        raise ValueError( 'Rank expected an integer between 2 and 9:', rank )

    key = 'get_m2_classes_' + str( ( rank, perm ) )
    if key in nt.get_tool_dct():
        return nt.get_tool_dct()[key]

    d = Div( [3] + ( rank - 1 ) * [-1] )
    m2_lst = get_div_set( d, 0, -2, perm )
    if perm:
        for comb in Combinations( range( 1, rank ), 2 ):
            m2_lst += [ Div.new( str( comb[0] ) + str( comb[1] ), rank ) ]
    else:
        m2_lst += [ Div.new( '12', rank ) ]

    m2_lst.sort()

    # cache generated data in file
    nt.get_tool_dct()[key] = m2_lst
    nt.save_tool_dct()

    return m2_lst


def get_m1_classes( rank, perm = False, d_lst = [] ):
    '''
    INPUT:
        - "rank" -- An integer between 3 and 9.
        - "perm" -- A boolean.
        - "d_lst" -- A list of lists of "Div" objects "d", 
                     such that d*d=-2 and d*(3e0-e1-...-er)=0 
                     where r=rank-1.
                     We assume that the matrix of the intersection
                     product of these divisors is a diagonal matrix
                     with signature (-1,1,...,1).        
    OUTPUT:
        - Returns a sorted list of "Div" objects "q", 
          such that 
              q*q=q*(-3e0+e1+...+er)=-1 
          and q*d >=0 for all d in "d_lst".
    '''
    if rank not in range( 3, 9 + 1 ):
        raise ValueError( 'Rank expected an integer between 3 and 9:', rank )

    key = 'get_m1_classes_' + str( ( rank, perm, d_lst ) )
    if key in nt.get_tool_dct():
        return nt.get_tool_dct()[key]

    # construct (-1) classes
    d = Div( [3] + ( rank - 1 ) * [-1] )
    m1t_lst = copy( get_div_set( d, 1, -1, perm ) )
    if perm:
        m1t_lst += [Div.new( 'e' + str( i ), rank ) for i in range( 1, rank )]
    else:
        m1t_lst += [Div.new( 'e1', rank )]

    # construct (-1)-classes that are positive against "d_lst"
    m1_lst = []
    for m1t in m1t_lst:
        indecomp = True
        for d in d_lst:
            if d * m1t < 0:
                indecomp = False
                break  # out of for loop
        if indecomp:
            m1_lst += [m1t]

    m1_lst.sort()
    nt.p( 'd_lst =', d_lst, ', m1_lst =', m1_lst )

    # cache generated data in file
    nt.get_tool_dct()[key] = m1_lst
    nt.save_tool_dct()

    return m1_lst


def get_fam_classes( rank, perm = False, d_lst = [] ):
    '''
    INPUT:
        - "rank"  -- An integer between 3 and 9.
        - "perm"  -- A boolean.
        - "d_lst" -- A list of lists of "Div" objects "d", 
                     such that d*d=-2 and d*(-3e0+e1+...+er)=0 
                     where r=rank-1.
                     We assume that the matrix of the intersection
                     product of these divisors is a diagonal matrix
                     with signature (-1,1,...,1).        
    OUTPUT:
        - Returns a sorted list of "Div" objects "f", 
          such that 
              f*f=0 and f*(3e0-e1-...-er)=2 
          and f*d >=0 for all d in "d_lst".
    '''
    if rank not in range( 3, 9 + 1 ):
        raise ValueError( 'Rank expected an integer between 3 and 9:', rank )

    key = 'get_fam_classes_' + str( ( rank, perm, d_lst ) )
    if key in nt.get_tool_dct():
        return nt.get_tool_dct()[key]

    # construct "Div" objects s.t. f*f=0 and d*f=2
    d = Div( [3] + ( rank - 1 ) * [-1] )
    ft_lst = get_div_set( d, 2, 0, perm )


    # check positivity against "d_lst"
    f_lst = []
    for f in ft_lst:
        indecomp = True
        for d in d_lst:
            if d * f < 0:
                indecomp = False
                break  # out of for loop
        if indecomp:
            f_lst += [f]

    f_lst.sort()

    # cache generated data in file
    nt.get_tool_dct()[key] = f_lst
    nt.save_tool_dct()

    return f_lst


