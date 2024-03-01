'''
    Graph Class
'''

import graphpy.vertex as vertex
import graphpy.edge as edge
import graphpy.graph_utils as graph_utils
from graphpy.search_strategy import SearchStrategy


class Graph(object):
    """Class to store a edges's array and a vertex's dictionary"""

    def __init__(self, directed=False):
        """create a object graph
            directed (bool, optional): Defaults to False.
                tells if the graph is directed or not
        """

        self.__edges = {}  # tupla diccionary (no source, no dest)
        self.__adjacent_list = {}
        self.__directed = directed

        self.__distance = {}  # guarda a distancia entre os vertices (bfs)
        self.__predecessors = {}  # predecessores do vertex [bfs]

    # Validate types

    def __check_vertex(self, vtx, field):
        if not isinstance(vtx, vertex.Vertex):
            raise TypeError(field + " must be of type 'Vertex'")
        if vtx not in self.__adjacent_list.keys():
            raise ValueError(field + " not found in the graph")

    def __check_edge(self, edg, field):
        if not isinstance(edg, edge.Edge):
            raise TypeError(field + " must be of type 'Edge'")
        if edg not in self.__edges.values():
            raise ValueError(field + " not found in the graph")

    # Operators overloading

    def __len__(self):
        return len(self.__adjacent_list)

    def __getitem__(self, vtx_name):
        return self.get_vertex(vtx_name)

    def __str__(self):
        return str(self.__adjacent_list)

    def __repr__(self):
        return str(self.__adjacent_list)

    # edge function
    # start here

    def add_edge(self, source, destination, label=None, value=1):
        """add a new connetion to the graph

        connects two vertex, if the graph is directed, this connection leaves
        the origin until the destination only.
        if the graph is not directed, the connection will be both the source
        to the destination as the destination to the source

        Args:
            source (Vertex): a source vertex
            destination (Vertex): a destination vertex
            label (stg, optional): Defaults to None. A label to this connection
            value (float, optional): Defaults to None.
                A value to this connection
        """

        self.__check_vertex(source, "source")
        self.__check_vertex(destination, "destination")

        # create a new edge
        new_edge = edge.Edge(source, destination, label=label, value=value)

        # test if the destination isn't connected with the source
        if destination not in self.__adjacent_list[source]:
            # insert source
            if new_edge.get_source() not in self.__adjacent_list:
                self.__adjacent_list[new_edge.get_source()] = []
            # insert destination
            if new_edge.get_destination() not in self.__adjacent_list:
                self.__adjacent_list[new_edge.get_destination()] = []

            # insert edge and update adjacent list
            self.__edges[(new_edge.get_source(),
                          new_edge.get_destination())] = new_edge
            self.__adjacent_list[new_edge.get_source()].append(
                new_edge.get_destination())

        # if not directed.. do the same with the other node
        if not self.__directed:
            if source not in self.__adjacent_list[destination]:
                self.__edges[(new_edge.get_destination(),
                              new_edge.get_source())] = new_edge
                self.__adjacent_list[new_edge.get_destination()].append(
                    new_edge.get_source())

    def remove_edge(self, edge_to_remove):
        """remove a connection from the graph

        Args:
            edge_to_remove (Edge): a edge (connection) that you want to remove
        """

        self.__check_edge(edge_to_remove, "edge_to_remove")

        self.__adjacent_list[edge_to_remove.get_source()].remove(
            edge_to_remove.get_destination())
        self.__edges.pop(
            (edge_to_remove.get_source(), edge_to_remove.get_destination())
        )
        if not self.__directed:
            self.__adjacent_list[edge_to_remove.get_destination()].remove(
                edge_to_remove.get_source())
            self.__edges.pop(
                (edge_to_remove.get_destination(), edge_to_remove.get_source())
            )

    def get_all_edges(self):
        """Return all the edges on the graph

        Returns:
            list: return a list with all the edges
        """

        edges = []
        for key in self.__edges:
            if (self.__edges[key] not in edges):
                edges.append(self.__edges[key])

        return edges

    def get_edge_from_souce_destination(self, source, destination):
        """Get a edge from a source and a destination vertex

        Args:
            source (Vertex): a source vertex from the connetion
            destination (Vertex): a destination vertex from the connetion

        Returns:
            Edge: return the egde that maches with the source and destination
                or return None
        """

        self.__check_vertex(source, "source")
        self.__check_vertex(destination, "destination")

        if self.__edges[(source, destination)]:
            return self.__edges[(source, destination)]
        return None
    # end here

    # Vertex functions
    # start here
    def add_vertex(self, name, value=None):
        """Add a new vertex to the graph

        Args:
            name (str): a name to the new vertex
            value (float, optional): Defaults to None.
                a value to the new vertex
        """

        for key in self.__adjacent_list:
            if key.get_name() == name:
                return

        new_vertex = vertex.Vertex(name, value=None)
        self.__adjacent_list[new_vertex] = []

    def get_vertex(self, name):
        """get a vertex from the graph

        Args:
            name (str): name of the vertex that you want

        Returns:
            Vertex: return a vertex that matches with the name, or return None
        """

        for key in self.__adjacent_list:
            if key.get_name() == name:
                return key
        return None

    def get_all_vertex(self):
        """Return all the vertex on the graph

        Returns:
            list: return a list with all the vertex
        """

        vertex = []
        for key in self.__adjacent_list:
            vertex.append(key)

        return vertex

    def adjacents_vertex(self, vtx):
        """Get the list of adjacents from a vertex

        Args:
            vtx (vertex): vertex you want to know the adjacent

        Returns:
            list: list of all adjacents of a vertex
        """
        self.__check_vertex(vtx, "vtx")

        return self.__adjacent_list[vtx]

    def remove_vertex(self, vertex_to_remove):
        """Remove a vertex and all the connections he have

        Args:
            vertex_to_remove (Vertex): vertex you want to remove
        """

        self.__check_vertex(vertex_to_remove, "vertex_to_remove")

        for key in self.__adjacent_list:
            if vertex_to_remove in self.__adjacent_list[key]:
                self.__adjacent_list[key].remove(vertex_to_remove)
        self.__adjacent_list.pop(vertex_to_remove, None)
        for key in list(self.__edges):
            if vertex_to_remove in key:
                self.__edges.pop(key, None)
    # end here

    def print_adjacent_list(self):
        """Print the adjacent list, A.K.A the graph
        """

        print(self.__adjacent_list)

    def get_order(self):
        """Return o order of the graph

        Returns:
            int: return the order of the graph
        """

        return len(self.__adjacent_list)

    def search(self, searchStrategy):
        if not isinstance(searchStrategy, SearchStrategy):
            raise TypeError("search strategy must be of type 'SearchStrategy'")

        searchStrategy.setup(self.__adjacent_list)
        return searchStrategy.search()

    def dijkistra(self, initial_vertex):
        for key in self.__adjacent_list:
            if key != initial_vertex:
                self.__distance[key] = float("inf")
                self.__predecessors[key] = None
        self.__distance[initial_vertex] = 0
        nodes = list(self.__adjacent_list.keys())
        while len(nodes) != 0:
            node = graph_utils.get_min(nodes, self.__distance)
            for adjacent in self.__adjacent_list[node]:
                value = (self.__distance[node] +
                         self.get_edge_from_souce_destination(node, adjacent)
                         .get_value())
                if (self.__distance[adjacent] > value):
                    self.__distance[adjacent] = value
                    self.__predecessors[adjacent] = node
        return self.__distance

    def in_degree_vertex(self, vtx):
        """Get the in degree of a vertex

        Args:
            vtx (Vertex): vertex you want know the degree

        Returns:
            integer: in degree of a vertex
        """

        self.__check_vertex(vtx, "vtx")

        if self.__directed:
            inVertex = 0
            for key in self.__adjacent_list:
                if vtx in self.__adjacent_list[key]:
                    inVertex = inVertex + 1
            return inVertex
        else:
            return len(self.__adjacent_list[vtx])

    def degree_vertex(self, vtx):
        """Get the degree of a vertex

        Args:
            vtx (Vertex): vertex you want know the degree

        Returns:
            integer: degree of a vertex
        """

        self.__check_vertex(vtx, "vtx")

        if self.__directed:
            inVertex = 0
            outVertex = len(self.__adjacent_list[vtx])
            for key in self.__adjacent_list:
                if vertex in self.__adjacent_list[key]:
                    inVertex = inVertex + 1
            return outVertex + inVertex
        else:
            return len(self.__adjacent_list[vtx])

    def is_completed(self):
        """tell if a graph is completed or not

        Returns:
            Bool: return if the graph is completed
        """

        for node in self.__adjacent_list:
            for key in self.__adjacent_list:
                if node != key:
                    if node not in self.__adjacent_list[key]:
                        return False
        return True


if __name__ == '__main__':
    from BFSstrategy import BFSstrategy
    graph = Graph()
    graph.add_vertex('teste')
    graph.add_vertex('teste1')
    graph.add_vertex('teste2')
    graph.add_edge(graph.get_vertex('teste'), graph.get_vertex('teste2'))
    print(graph)
    # print(graph.search(BFSstrategy(graph['teste'])))
    # print(graph.adjacents_vertex(graph.get_vertex('teste')))
    # print(graph.get_order())
    # print(graph.get_all_edges())
    # print("len:", len(graph))
    # myEdge = graph.get_edge_from_souce_destination(
    #     graph.get_vertex('teste'), graph.get_vertex('teste2'))
    # graph.remove_edge(myEdge)
    # graph.remove_vertex(graph.get_vertex('teste'))
    # print(graph.get_all_edges())
    # graph.print_adjacent_list()
