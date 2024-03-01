'''
Created on Aug 4, 2016
@author: Niels Lubbes
'''
from sage.all import *

import inspect
import time
import sys


# global variable used by "ns_tools.get_tool_dct()" and "ns_tools.save_tool_dct()"
tool_dct = None

# global variable used by "ns_tools.np()"
input_file_name = None



def get_tool_dct( fname = "ns_tools" ):
    '''
    INPUT:
        - "fname" -- Name of file without extension.
    OUTPUT:
        - Loads global variable "tool_dct" 
          in memory from file "<local path>/<fname>.sobj"
          if called for the first time.
          
        - Returns "tool_dct".
    '''
    path = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
    file_name = path + fname
    global tool_dct
    if tool_dct == None:
        try:
            # raise
            np( 'Loading from:', file_name )
            tool_dct = load( file_name )
        except Exception as e:
            np( 'Cannot load "tool_dct": ', e )
            tool_dct = {}

    return tool_dct


def save_tool_dct( fname = "ns_tools" ):
    '''
    INPUT:
        - "fname" -- Name of file without extension.        
    OUTPUT:
        - Saves global "tool_dct" to  "fname".
    '''
    path = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
    file_name = path + fname
    global tool_dct

    np( 'Saving to:', file_name )
    save( tool_dct, file_name )


def np( *arg_lst ):
    '''
    INPUT:
        - "*arg_lst" -- List of arguments.
    OUTPUT:
        - * np(True): from now on all "np" calls are handled.
          * np(False, [file_name] ): only calls from [file_name] are handled. 
          * Otherwise prints arguments to "sys.stdout" together with  
            reflection info from "inspect.stack()".
        - Returns output string, or "None" if "arg_lst[0]" is "True" or "False".
    '''
    global input_file_name

    # check arguments
    if type( arg_lst[0] ) == type( True ):  # note that 0==False
        if arg_lst[0] == False:
            if len( arg_lst ) != 2:
                raise ValueError( 'If the 1st argument equals "False" then ' +
                                  'the 2nd argument is ' +
                                  'expected to be a file name. ', arg_lst )
            input_file_name = arg_lst[1]
            np( input_file_name )
            return None
        elif arg_lst[0] == True:
            input_file_name = None
            return None

    # collect relevant info from stack trace
    sk_lst_lst = inspect.stack()
    file_name = str( sk_lst_lst[1][1] )
    line = str( sk_lst_lst[1][2] )
    method_name = str( sk_lst_lst[1][3] )

    # only output when op is called from "op.input_file_name"
    if input_file_name != None:
        if not file_name.endswith( input_file_name ):
            return

    # construct output string
    s = method_name + '(' + line + ')' + ': '
    for arg in arg_lst:
        s += str( arg ) + ' '

    # print output
    print s
    sys.stdout.flush()

    return s

def nt( start = False ):
    '''
    INPUT:
        - "start" -- A boolean.
    OUTPUT:
        - If "start==True" then 0 is printed to "sys.stdout". 
          If "start==False" then outputs the following to "sys.stdout": 
          seconds passed since the last "nt(True)" call.       
          The outputs also contain reflection info from "inspect.stack()".
        - Returns output string.
    '''
    # get time
    if start:
        nt.t0 = time.clock()  # set static variable.
        dt = 0
    else:
        ct = time.clock()
        dt = ct - nt.t0
        nt.t0 = ct

    # collect relevant info from stack trace
    sk = inspect.stack()
    line = str( sk[1][2] )
    method_name = str( sk[1][3] )

    # construct output string
    s = method_name + '(' + line + ')[' + str( dt ) + ']'
    print s
    sys.stdout.flush()

    return s

