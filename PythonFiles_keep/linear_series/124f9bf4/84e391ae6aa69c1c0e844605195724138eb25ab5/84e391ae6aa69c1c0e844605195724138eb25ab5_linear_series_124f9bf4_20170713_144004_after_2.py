'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 12, 2017
@author: Niels Lubbes
'''


class TestTools( object ):

    def __clean__( self, str0, s_lst ):
        for s in s_lst:
            while s in str0:
                str0 = str0.replace( s, '' )
        return str0


    def equal_output_strings( self, str1, str2, s_lst = ' \n\t' ):
        '''
        This method can be used to test outputs of methods, 
        where the output is considered as a String and where 
        characters such as spaces, newlines or tabs do not 
        matter for testing the correctness. 
                
        INPUT:
            - str1   -- A String.
            - str2   -- A String.
            - s_lst  -- A list of strings. A String is considered as 
                        a list of strings of lenght one (ie. characters).
        OUTPUT:
            - Returns True if "str1" and "str2" are equal after we replace 
              all occurrences of strings in "s_lst" with the empty string ''.  
              This method returns False otherwise.
        '''

        return self.__clean__( str1, s_lst ) == self.__clean__( str2, s_lst )



if __name__ == '__main__':

    # print( TestTools().equal_output_strings( 'a', 'b' ) )
    pass

