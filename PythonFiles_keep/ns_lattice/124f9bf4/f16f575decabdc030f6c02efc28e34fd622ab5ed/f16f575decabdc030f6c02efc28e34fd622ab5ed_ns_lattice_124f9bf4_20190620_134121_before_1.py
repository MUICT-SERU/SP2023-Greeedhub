'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 27, 2018

@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_n

from ns_lattice.class_ns_tools import NSTools

import time


class ETA( object ):
    '''
    For estimating the time it takes for a loop in a program to terminate 
    (ETA=estimated time of arrival).
    During the loop feedback is printed.  
    '''

    def __init__( self, total, ival ):
        '''

        Should be called before a loop in the program starts.        
        
        Parameters
        ----------
        total: int
            Number of times the loop needs to be traced.
        
        ival : int
            Nonzero number of traced loops in program until
            feedback about etimated end time is printed        
        '''
        self.ostart = time.time()  # start time
        self.total = total  # total number of loops
        self.ival = 1
        if ival > 0:
            self.ival = ival  # number of loops after which eta is updated
        self.counter = 0  # loop counter
        self.istart = None  # start time which is updated after ival loops.
        self.eta = None  # estimated time of arrival in minutes


    def update( self, *info_lst ):
        '''
        Prints an estimation for the time it takes for a program to 
        terminate (ETA for short). We refer to the program termination 
        as arrival.
        
        Parameters
        ----------
        *info_lst : string
            Variable length argument list consisting of 
            additional information that is printed together with ETA.
        '''
        if self.counter % self.ival == 0:
            self.istart = time.time()

        self.counter += 1

        if self.counter % self.ival == 0:

            itime = ( time.time() - self.istart ) / ( 60 * self.ival )
            otime = sage_n( ( time.time() - self.ostart ) / 60, digits = 5 )
            self.eta = sage_n( itime * ( self.total - self.counter ), digits = 5 )

            s = ''
            for info in info_lst:
                s += str( info ) + ' '

            NSTools.p( 'ETA =', self.eta, 'm,',
                       'counter =', self.counter, '/', self.total, ',',
                       'time =', otime, 'm,',
                       'info =', s )


