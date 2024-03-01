'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 8, 2017
@author: Niels Lubbes

'''

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.convert_to_tex import cls_to_tex


class TestConvertToTex:


    def test__cls_to_tex( self ):

        if 'get_CLS9' not in NSTools.get_tool_dct():
            return
        out = cls_to_tex()
        print( out )


if __name__ == '__main__':

    NSTools.filter( None )

    TestConvertToTex().test__cls_to_tex()

    pass
