'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 7, 2017
@author: Niels Lubbes
'''

import inspect
import time
import sys


class NSTools():
    '''
    
    For accessing static variables in python see for example:
    <http://stackoverflow.com/questions/11759269/calling-static-method-in-python>
    '''

    # private dictionary object used by ".get_tool_dct()"
    __tool_dct = None

    # private variable for timer
    __start_time = None
    __end_time = None

    # private static variables used by ".verbose()"
    __filter_fname = None
    __prev_filter_fname = None


    @staticmethod
    def filter( filter_fname ):
        '''
        INPUT:
            - "filter_fname" -- File name 
        '''
        NSTools.__filter_fname = filter_fname
        NSTools.__prev_filter_fname = filter_fname

    @staticmethod
    def filter_unset():
        '''
        Output via ".out" will not be surpressed.
        '''
        NSTools.__filter_fname = None

    @staticmethod
    def filter_reset():
        '''
        Resets filter state to before previous ".filter_unset()" call.
        '''
        NSTools.__filter_fname = NSTools.__prev_filter_fname

    @staticmethod
    def p( *arg_lst ):
        '''
        INPUT:
            - "*arg_lst" -- List of arguments.
        OUTPUT:
            - If ".filter_on(<fname>)" has been called and the file name
              of the calling module does not coincide with <fname>
              then the output is surpressed.
              
              Otherwise, this method prints arguments to "sys.stdout" 
              together with reflection info from "inspect.stack()".
              
              Call ".filter_off()" to turn off filter, such that
              all output is send to "sys.stdout".  
                                   
        '''
        # collect relevant info from stack trace
        sk_lst_lst = inspect.stack()
        file_name = str( sk_lst_lst[1][1] )
        line = str( sk_lst_lst[1][2] )
        method_name = str( sk_lst_lst[1][3] )

        # only output when op is called from "op.input_file_name"
        if NSTools.__filter_fname != None:
            if not file_name.endswith( NSTools.__filter_fname ):
                return

        # construct output string
        s = method_name + '(' + line + ')' + ': '
        for arg in arg_lst:
            s += str( arg ) + ' '

        # print output
        print s
        sys.stdout.flush()

        return s


    @staticmethod
    def get_tool_dct( fname = 'ns_tools' ):
        '''
        INPUT:
            - "fname" -- Name of file without extension.
        OUTPUT:
            - Sets static private variable "__tool_dct" 
              in memory from file "<local path>/<fname>.sobj"
              if called for the first time.
              
            - Returns "__tool_dct".
        '''

        path = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
        file_name = path + fname
        if NSTools.__tool_dct == None:

            NSTools.unset()
            try:

                NSTools.p( 'Loading from:', file_name )
                NSTools.__tool_dct = load( file_name )

            except Exception as e:

                NSTools.p( 'Cannot load ".__tool_dct": ', e )
                NSTools.__tool_dct = {}

            NSTools.reset()

        return NSTools.__tool_dct


    @staticmethod
    def save_tool_dct( fname = 'ns_tools' ):
        '''
        INPUT:
            - "fname" -- Name of file without extension.        
        OUTPUT:
            - Saves "__tool_dct" to  "fname".
        '''
        path = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
        file_name = path + fname

        NSTools.filter_unset()
        NSTools.p( 'Saving to:', file_name )
        NSTools.filter_reset()

        save( NSTools.__tool_dct, file_name )


    @staticmethod
    def start_timer():
        '''
        OUTPUT:
            - Prints the current time and starts timer.
        '''
        # get time
        NSTools.__start_time = time.clock()  # set static variable.

        NSTools.filter_unset()
        NSTools.p( 'start time =', NSTools.__start_time )
        NSTools.filter_reset()


    @staticmethod
    def end_timer():
        '''
        OUTPUT:
            - Prints time passed since last call of ".start_timer()".
        '''
        NSTools.__end_time = time.clock()
        passed_time = NSTools.__end_time - NSTools.__start_time

        NSTools.filter_unset()
        NSTools.p( 'time passed =', passed_time )
        NSTools.filter_reset()




