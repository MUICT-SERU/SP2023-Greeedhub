'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 7, 2017
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_matrix

from ns_lattice.class_div import Div

from ns_lattice.dp_involutions import complete_basis
from ns_lattice.sage_interface import sage_vector
from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_ak
from ns_lattice.class_eta import ETA
from ns_lattice.sage_interface import sage_ZZ


from ns_lattice.dp_root_bases import get_dynkin_type

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


    def test__get_marked_Mtype( self ):
        NSTools.set_enable_tool_dct( False )

        # (2A1, 4A1) Neron-Severi lattice of ring torus
        rank = 6
        d_lst = [ 'e2-e4', 'e3-e5', 'e0-e1-e2-e4', 'e0-e1-e3-e5']
        Md_lst = ['e4-e5', 'e0-e1-e2-e3']
        M = [( 2, 1, 1, 1, 0, 0 ), ( -1, 0, -1, -1, 0, 0 ), ( -1, -1, 0, -1, 0, 0 ), ( -1, -1, -1, 0, 0, 0 ), ( 0, 0, 0, 0, 0, 1 ), ( 0, 0, 0, 0, 1, 0 )]
        d_lst = [ Div.new( d, rank ) for d in d_lst ]
        Md_lst = [ Div.new( Md, rank ) for Md in Md_lst ]
        M = sage_matrix( M )
        dpl = DPLattice( d_lst, Md_lst, M )

        print( dpl.get_marked_Mtype() )
        print( dpl.Mtype )

        assert dpl.get_marked_Mtype() == "2A1'"
        NSTools.set_enable_tool_dct( True )


    def test__get_bas_lst__rank_3( self ):
        NSTools.set_enable_tool_dct( False )
        bas_lst = DPLattice.get_bas_lst( 3 )
        assert len( bas_lst ) == 2
        for bas in bas_lst:
            print( bas )
        print( len( bas_lst ) )
        NSTools.set_enable_tool_dct( True )


    def test__get_bas_lst__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        bas_lst = DPLattice.get_bas_lst( 4 )
        for bas in bas_lst:
            print( bas )

        print( len( bas_lst ) )
        assert len( bas_lst ) == 6

        type_lst = []
        for bas in bas_lst:
            type_lst += [( bas.Mtype, bas.type )]
        print( type_lst )
        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A0', 'A1'), ('A0', '2A1'), ('A0', 'A2'), ('A0', 'A1+A2')]"

        NSTools.set_enable_tool_dct( True )


    def test__get_inv_lst__rank_4( self ):
        NSTools.set_enable_tool_dct( False )
        rank = 4
        inv_lst = DPLattice.get_inv_lst( rank )
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


    def test__get_cls_slow__rank_3( self ):
        NSTools.set_enable_tool_dct( False )

        rank = 3
        dpl_lst = DPLattice.get_cls_slow( rank )

        for dpl in dpl_lst:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )
        print( type_lst )

        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )


    def test__get_cls_slow__rank_4( self ):
        NSTools.set_enable_tool_dct( False )

        rank = 4
        dpl_lst = DPLattice.get_cls_slow( rank )

        for dpl in dpl_lst:
            dpl.set_attributes( 8 )

        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( type_lst[-1] )
        print( type_lst )

        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A0', 'A1'), ('A0', '2A1'), ('A0', 'A2'), ('A0', 'A1+A2'), ('A1', 'A0'), ('A1', 'A1'), ('A1', 'A0'), ('A1', 'A1'), ('A1', 'A2'), ('2A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )


    def test__get_num_types( self ):

        NSTools.set_enable_tool_dct( False )
        bas_lst = DPLattice.get_bas_lst( 4 )
        inv_lst = DPLattice.get_inv_lst( 4 )

        bas = bas_lst[1]
        inv = inv_lst[-1]
        assert inv.Mtype == '2A1'
        assert bas.type == 'A1'
        assert DPLattice.get_num_types( inv, bas, bas_lst ) == 0

        bas = bas_lst[1]
        inv = inv_lst[2]
        assert inv.Mtype == 'A1'
        assert bas.type == 'A1'
        assert DPLattice.get_num_types( inv, bas, bas_lst ) == -1

        NSTools.set_enable_tool_dct( True )


    def test__get_part_roots( self ):
        NSTools.set_enable_tool_dct( False )
        inv_lst = DPLattice.get_inv_lst( 4 )
        inv = inv_lst[1]
        assert inv.Mtype == 'A1'

        s_lst, q_lst = DPLattice.get_part_roots( inv )
        assert len( s_lst ) == 1
        assert q_lst == []

        NSTools.set_enable_tool_dct( True )


    def test__seek_bases( self ):
        NSTools.set_enable_tool_dct( False )

        bas = DPLattice.get_bas_lst( 4 )[-1]
        assert bas.type == 'A1+A2'

        inv = DPLattice.get_inv_lst( 4 )[0]
        assert inv.Mtype == 'A0'

        r_lst = get_divs( get_ak( bas.get_rank() ), 0, -2, True )

        dpl_lst = DPLattice.seek_bases( inv, bas.d_lst, r_lst )

        for dpl in dpl_lst:
            dpl.set_attributes()
            print( dpl.Mtype, dpl.type, dpl.d_lst )

        assert len( dpl_lst ) == 1

        NSTools.set_enable_tool_dct( True )


    def test__get_cls__rank_3( self ):
        NSTools.set_enable_tool_dct( False )

        dpl_lst = DPLattice.get_cls( 3 )
        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
        print( type_lst )

        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A1', 'A0')]"
        NSTools.set_enable_tool_dct( True )


    def test__import_cls( self ):
        NSTools.set_enable_tool_dct( False )

        dpl_lst = DPLattice.get_cls( 3 )
        type_lst = [( dpl.Mtype, dpl.type ) for dpl in dpl_lst ]
        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A1', 'A0')]"

        inv = DPLattice.get_inv_lst( 4 )[1]
        assert inv.Mtype == 'A1'

        out_lst = DPLattice.import_cls( dpl_lst, inv )

        assert len( out_lst ) == 1
        assert out_lst[0].get_rank() == 4
        assert out_lst[0].Mtype == 'A1'
        assert out_lst[0].type == 'A0'

        NSTools.set_enable_tool_dct( True )


    def test__get_cls__rank_4( self ):
        NSTools.set_enable_tool_dct( False )

        dpl_lst = DPLattice.get_cls( 4 )
        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.Mtype, dpl.type )]
            print( dpl.get_marked_Mtype(), dpl.type )

        print( type_lst )
        assert str( type_lst ) == "[('A0', 'A0'), ('A0', 'A1'), ('A0', 'A1'), ('A0', '2A1'), ('A0', 'A2'), ('A0', 'A1+A2'), ('A1', 'A0'), ('A1', 'A1'), ('A1', 'A0'), ('A1', 'A1'), ('A1', 'A2'), ('2A1', 'A0')]"

        NSTools.set_enable_tool_dct( True )


    def test__get_real_type( self ):
        NSTools.set_enable_tool_dct( False )

        dpl_lst = DPLattice.get_cls_slow( 4 )

        type_lst = []
        for dpl in dpl_lst:
            type_lst += [( dpl.get_marked_Mtype(), dpl.get_real_type() )]

        out = ''
        for type in type_lst:
            print( type[0] + ', ' + type[1] )
            out += type[0] + ',' + type[1] + '; '
        print( out )

        assert out.strip() == "A0,A0; A0,{A1}; A0,{A1}; A0,2{A1}; A0,{A2}; A0,{A1}+{A2}; A1,A0; A1,{A1}; A1',A0; A1',{A1}; A1',{A2}; 2A1,A0;"

        NSTools.set_enable_tool_dct( True )


    def test__are_root_bases( self ):

        NSTools.set_enable_tool_dct( False )
        bas_lst = DPLattice.get_bas_lst( 4 )


        for bas in bas_lst:
            if bas.d_lst == []:
                continue

            mat = complete_basis( bas.d_lst )
            r_lst = get_divs( get_ak( bas.get_rank() ), 0, -2, True )

            print( bas.type, bas.d_lst, 10 * '=' )
            for r in r_lst:
                vec = ~mat * sage_vector( r.e_lst )
                print( r.e_lst, vec, r, list( mat ) )

                in_span = set( vec[len( bas.d_lst ):] ) == {0}
                zz_coef = set( [elt in sage_ZZ for elt in vec ] ) == {True}
                pos_coef = set( [elt >= 0 for elt in vec] ) == {True}

                if in_span and zz_coef:
                    assert pos_coef

        NSTools.set_enable_tool_dct( True )


if __name__ == '__main__':

    NSTools.filter( None )
    # NSTools.filter( ['class_dp_lattice.py', 'class_eta.py'] )


    # TestClassDPLattice().test__eq()
    # TestClassDPLattice().test__get_marked_Mtype()
    TestClassDPLattice().test__get_bas_lst__rank_3()
    # TestClassDPLattice().test__get_bas_lst__rank_4()
    # TestClassDPLattice().test__get_inv_lst__rank_4()
    # TestClassDPLattice().test__get_cls_slow__rank_3()
    # TestClassDPLattice().test__get_cls_slow__rank_4()

    # TestClassDPLattice().test__get_num_types()
    # TestClassDPLattice().test__get_part_roots()
    # TestClassDPLattice().test__seek_bases()
    # TestClassDPLattice().test__import_cls()

    # TestClassDPLattice().test__get_cls__rank_3()
    # TestClassDPLattice().test__get_cls__rank_4()
    # TestClassDPLattice().test__get_real_type()
    # TestClassDPLattice().test__are_root_bases()

    pass

