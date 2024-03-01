'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 7, 2017
@author: Niels Lubbes
'''

from nose import with_setup  # optional

from linkage import *



class TestClassLinkageGraph:


    def test_get_line_symmetric_icosahedron_returns_graph_with_consistent_edges( self ):
        lg = LinkageGraph.get_line_symmetric_icosahedron()

        edge_lst = [( 0, 1 ), ( 0, 5 ), ( 0, 7 ), ( 0, 8 ), ( 0, 11 ), ( 1, 2 ),
                    ( 1, 5 ), ( 1, 6 ), ( 1, 8 ), ( 2, 3 ), ( 2, 6 ), ( 2, 8 ),
                    ( 2, 9 ), ( 3, 4 ), ( 3, 6 ), ( 3, 9 ), ( 3, 10 ), ( 4, 5 ),
                    ( 4, 6 ), ( 4, 10 ), ( 4, 11 ), ( 5, 6 ), ( 5, 11 ), ( 7, 8 ),
                    ( 7, 9 ), ( 7, 10 ), ( 7, 11 ), ( 8, 9 ), ( 9, 10 ), ( 10, 11 )]
        assert lg.G.edges( labels = False ) == edge_lst


    def test_set_random_edge_labels_2_4( self ):
        lg = LinkageGraph.get_line_symmetric_icosahedron()
        lg.set_random_edge_labels( 2, 4 )
        for edge_len in lg.G.edge_labels():
            assert edge_len >= 2 and edge_len <= 4




