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
        NSTools.set_enable_tool_dct( False )

        Md_lst = []
        M = sage_identity_matrix( sage_QQ, 4 )

        dpl23 = DPLattice( [Div.new( '23', 4 )], Md_lst, M )
        dpl1123 = DPLattice( [Div.new( '1123', 4 )], Md_lst, M )
        dpl12 = DPLattice( [Div.new( '12', 4 )], Md_lst, M )

        assert dpl23 != dpl1123
        assert dpl23 == dpl12

        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases__rank_3( self ):
        NSTools.set_enable_tool_dct( False )
        bas_lst = DPLattice.get_cls_root_bases( 3 )
        print( len( bas_lst ) )
        for dpl in bas_lst:
            print( dpl )
        assert len( bas_lst ) == 2
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        rank = 4
        bas_lst = DPLattice.get_cls_root_bases( rank )
        print( len( bas_lst ) )
        for dpl in bas_lst:
            print( dpl )
        assert len( bas_lst ) == 6
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_root_bases__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        rank = 4
        bas_lst = DPLattice.get_cls_root_bases( rank )
        print( len( bas_lst ) )
        for dpl in bas_lst:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in bas_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )

        assert len( bas_lst ) == 6
        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A0', 'A1'), ('A0', '2A1'), ('A0', 'A2'), ('A0', 'A1+A2')]"
        NSTools.set_enable_tool_dct( True )

    def test__get_cls_involutions__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        rank = 4
        inv_lst = DPLattice.get_cls_involutions( rank )
        print( len( inv_lst ) )
        for inv in inv_lst:
            inv.set_attributes( 8 )

        type_lst = []
        for inv in inv_lst:
            type_lst += [( inv.Mtype, inv.type )]
            print( type_lst[-1] )

        assert len( inv_lst ) == 4
        assert str( type_lst ) == "[('A0', 'A0'), ('A1', 'A0'), ('A1', 'A0'), ('2A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )

    def test__get_cls_real_dp__rank_3( self ):
        NSTools.set_enable_tool_dct( False )

        rank = 3
        dpl_lst = DPLattice.get_cls_real_dp( rank )

        for dpl in dpl_lst:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )
        print( type_lst )

        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_real_dp__rank_4( self ):
        NSTools.set_enable_tool_dct( False )

        rank = 4
        dpl_lst = DPLattice.get_cls_real_dp( rank )

        for dpl in dpl_lst:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )
        print( type_lst )

        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A0', 'A1'), ('A0', '2A1'), ('A0', 'A2'), ('A0', 'A1+A2'), ('A1', 'A0'), ('A1', 'A0'), ('A1', 'A1'), ('A1', 'A1'), ('A1', 'A2'), ('2A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_real_dp__large_rank( self ):
        # comment for long computation
        return

        # NSTools.set_enable_tool_dct( False )
        NSTools.filter( None )

        rank = 5
        dpl_lst = DPLattice.get_cls_real_dp( rank )

        for dpl in dpl_lst:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )
        print( type_lst )
        print( len( dpl_lst ) )

        assert len( dpl_lst ) == 12  # 5=12, 6=
        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    NSTools.filter( 'class_dp_lattice.py' )

    TestClassDPLattice().test__eq()
    # TestClassDPLattice().test__get_cls_root_bases__rank_3()
    # TestClassDPLattice().test__get_cls_root_bases__rank_4()
    # TestClassDPLattice().test__get_cls_invo__rank_4()
    # TestClassDPLattice().test__get_cls_real_dp__rank_3()
    # TestClassDPLattice().test__get_cls_real_dp__rank_4()
    # TestClassDPLattice().test__get_cls_real_dp__large_rank()
    pass
