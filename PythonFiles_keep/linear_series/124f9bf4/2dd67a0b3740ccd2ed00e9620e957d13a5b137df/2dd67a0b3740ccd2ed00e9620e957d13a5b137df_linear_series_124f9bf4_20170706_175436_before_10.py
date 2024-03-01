'''
Created on Aug 4, 2016
@author: Niels Lubbes
'''
from sage.all import *

import inspect
import time
import sys


def dprint( *arg_lst ):
    '''
    INPUT:
        - "*arg_lst" -- List of arguments.
    OUTPUT:
        - * dprint(True): from now on all "dprint" calls are handled.
          * dprint(False, [file_name] ): only calls from [file_name] are handled. 
          * Otherwise prints arguments to "sys.stdout" together with  
            reflection info from "inspect.stack()".
        - Returns output string or "None" if "arg_lst[0]" is "True" or "False".
    '''
    # check arguments
    if type( arg_lst[0] ) == type( True ):  # note that 0==False
        if arg_lst[0] == False:
            if len( arg_lst ) != 2:
                raise ValueError( 'If the 1st argument equals "False" then ' +
                                  'the 2nd argument is ' +
                                  'expected to be a file name. ', arg_lst )
            dprint.input_file_name = arg_lst[1]
            if dprint.input_file_name == None:
                dprint.input_file_name = '<no output>'
            dprint( dprint.input_file_name )
            return None
        elif arg_lst[0] == True:
            dprint.input_file_name = None
            return None

    # collect relevant info from stack trace
    sk_lst_lst = inspect.stack()
    file_name = str( sk_lst_lst[1][1] )
    line = str( sk_lst_lst[1][2] )
    method_name = str( sk_lst_lst[1][3] )

    # only output when dprint is called from "dprint.input_file_name"
    if dprint.input_file_name != None:
        if not file_name.endswith( dprint.input_file_name ):
            return

    # construct output string
    s = method_name + '(' + line + ')' + ': '
    for arg in arg_lst:
        s += str( arg ) + ' '

    # print output
    print s
    sys.stdout.flush()

    return s

def tprint( start = False ):
    '''
    INPUT:
        - "start" -- A boolean.
    OUTPUT:
        - If "start==True" then 0 is printed to "sys.stdout". 
          If "start==False" then outputs the following to "sys.stdout": 
          seconds passed since the last "tprint(True)" call.       
          The outputs also contain reflection info from "inspect.stack()".
        - Returns output string.
    '''
    # get time
    if start:
        tprint.t0 = time.clock()  # set static variable.
        dt = 0
    else:
        ct = time.clock()
        dt = ct - tprint.t0
        tprint.t0 = ct

    # collect relevant info from stack trace
    sk = inspect.stack()
    line = str( sk[1][2] )
    method_name = str( sk[1][3] )

    # construct output string
    s = method_name + '(' + line + ')[' + str( dt ) + ']'
    print s
    sys.stdout.flush()

    return s

