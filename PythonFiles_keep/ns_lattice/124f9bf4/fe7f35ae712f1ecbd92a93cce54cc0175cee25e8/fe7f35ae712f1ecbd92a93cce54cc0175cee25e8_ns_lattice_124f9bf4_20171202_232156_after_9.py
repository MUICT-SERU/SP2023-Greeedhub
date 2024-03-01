'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 7, 2017
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_identity_matrix

from ns_lattice.class_div import Div

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_dp_lattice import DPLattice


class TestClassDPLattice():

    def test__eq( self ):
        Md_lst = []
        M = sage_identity_matrix( sage_QQ, 4 )

        dpl23 = DPLattice( [Div.new( '23', 4 )], Md_lst, M )
        dpl1123 = DPLattice( [Div.new( '1123', 4 )], Md_lst, M )
        dpl12 = DPLattice( [Div.new( '12', 4 )], Md_lst, M )

        assert dpl23 != dpl1123
        assert dpl23 == dpl12


    def test__get_cls_root_bases__rank_3( self ):
        NSTools.set_enable_tool_dct( False )
        dct = DPLattice.get_cls_root_bases( 3 )
        print( len( dct[3] ) )
        for dpl in dct[3]:
            print( dpl )
        assert len( dct[3] ) == 2
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        rank = 4
        dct = DPLattice.get_cls_root_bases( rank )
        print( len( dct[rank] ) )
        for dpl in dct[rank]:
            print( dpl )
        assert len( dct[rank] ) == 6
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        rank = 4
        dct = DPLattice.get_cls_root_bases( rank )
        print( len( dct[rank] ) )
        for dpl in dct[rank]:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dct[rank]:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )

        assert len( dct[rank] ) == 6
        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A0', 'A1'), ('A0', '2A1'), ('A0', 'A2'), ('A0', 'A1+A2')]"
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_real_dp__rank_3( self ):
        NSTools.set_enable_tool_dct( False )

        rank = 3
        dct = DPLattice.get_cls_real_dp( rank )

        for dpl in dct[rank]:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dct[rank]:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )
        print( type_lst )

        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_real_dp__rank_4( self ):
        NSTools.set_enable_tool_dct( False )

        rank = 4
        dct = DPLattice.get_cls_real_dp( rank )

        for dpl in dct[rank]:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dct[rank]:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )
        print( type_lst )

        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A0', 'A1'), ('A0', '2A1'), ('A0', 'A2'), ('A0', 'A1+A2'), ('A1', 'A0'), ('A1', 'A0'), ('A1', 'A1'), ('A1', 'A1'), ('A1', 'A2'), ('2A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    NSTools.filter( 'class_dp_lattice.py' )

    # TestClassDPLattice().test__get_cls_root_bases__rank_3()
    # TestClassDPLattice().test__get_cls_root_bases__rank_4()
    # TestClassDPLattice().test__get_cls_real_dp__rank_3()
    TestClassDPLattice().test__get_cls_real_dp__rank_4()
    pass
