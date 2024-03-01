import sys
from search_strategy import SearchStrategy
import vertex
if sys.version_info >= (3, 0):
    import queue
else:
    import Queue as queue


class BFSstrategy(SearchStrategy):
    def __init__(self, initial_vertex):
        if not isinstance(initial_vertex, vertex.Vertex):
            raise TypeError("initial_vertex must be of type 'Vertex'")

        self.__initial_vertex = initial_vertex
        self.__distance = {}
        self.__predecessors = {}

    def search(self):
        """Calculate the distance of all vertex from one
        if a vertex can't be reach by the initial vertex,
        the distance will be infinity.. (float("inf"))

        Args:
            initial_vertex (Vetex): calculate the distance of
                all vertices up to this initial vertex

        Returns:
            Dict: dictionaty with the key as the vertex and the body
                the distance from the initial vertex
        """
        if self.__initial_vertex not in self.get_adjacent_list():
            raise ValueError("initial_vertex not found in the graph")

        # colors:
        #   white: not visited
        #   grey: in the queue
        #   black: nothing more to do
        for key in self.get_adjacent_list():
            if key != self.__initial_vertex:
                # set color for all vertices except the initial one to white
                key.set_color(0)
                self.__distance[key] = float("inf")
                self.__predecessors[key] = None

        # if the initial_vertex is not a valid one,
        # all the vertex will have distance equals to infinity
        if not self.__initial_vertex:
            return self.__distance

        self.__initial_vertex.set_color(1)  # inital vertex color to grey
        self.__distance[self.__initial_vertex] = 0
        self.__predecessors[self.__initial_vertex] = None
        q = queue.Queue()
        q.put(self.__initial_vertex)  # insert in the queue the initial vertex

        while not q.empty():
            vertex = q.get()

            for v in self.get_adjacent_list()[vertex]:
                if v.get_color() == 0:  # if a vertex color is white
                    v.set_color(1)  # turn to grey
                    self.__distance[v] = self.__distance[vertex] + 1
                    self.__predecessors[v] = vertex
                    q.put(v)
            vertex.set_color(2)  # color to black

        return self.__distance, self.__predecessors
