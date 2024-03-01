'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 17, 2017
@author: Niels Lubbes
'''

from linear_series.class_ls_tools import LSTools


class TestClassLSTools:


    def test__p( self ):

        lst = LSTools()

        lst.filter( None )
        assert lst.p( 'Hello world!' ) != None

        lst.filter( ['another_class.py'] )
        assert lst.p( 'No output since called from another class.' ) == None

        lst.filter_unset()
        assert lst.p( 'Filter is disabled so output this string.' ) != None

        lst.filter_reset()
        assert lst.p( 'Filter is enabled again so do not output.' ) == None

        lst.filter( ['test_class_ls_tools.py'] )
        assert lst.p( 'Only output if called from this class' ) != None


    def test__tool_dct( self ):

        lst = LSTools()
        lst2 = LSTools()

        # watch out to not use the default file name
        # otherwise it might take long to load the data
        test_fname = 'test_tools'
        key = 'test__tool_dct'

        dct = lst.get_tool_dct( fname = test_fname )
        dct[key] = True
        lst.save_tool_dct( fname = test_fname )

        assert key in lst.get_tool_dct( fname = test_fname )
        assert key in lst2.get_tool_dct( fname = test_fname )

        lst.set_enable_tool_dct( False )
        assert key not in lst.get_tool_dct( fname = test_fname )
        assert key not in lst2.get_tool_dct( fname = test_fname )

        lst.set_enable_tool_dct( True )
        assert key in lst.get_tool_dct( fname = test_fname )
        assert key in lst2.get_tool_dct( fname = test_fname )


