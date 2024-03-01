from graphpy.search_strategy import SearchStrategy


class DFSstrategy(SearchStrategy):
    def __init__(self):

        self.__predecessors = {}
        self.__firstSee = {}
        self.__close = {}
        self.__time = 0

    def __dfs_visit(self, vertex):
        self.__time = self.__time + 1
        self.__firstSee[vertex] = self.__time
        vertex.set_color(1)

        for adjacent in self.get_adjacent_list()[vertex]:
            if adjacent.get_color() == 0:
                self.__predecessors[adjacent] = vertex
                self.__dfs_visit(adjacent)
        vertex.set_color(2)
        self.__time += 1
        self.__close[vertex] = self.__time

    def search(self):
        # colors:
        #   white: not visited
        #   grey: in the queue
        #   black: nothing more to do
        for key in self.get_adjacent_list():
            # set color for all vertices to white
            key.set_color(0)
            self.__predecessors[key] = None
        self.__time = 0
        for key in self.get_adjacent_list():
            if key.get_color() == 0:
                self.__dfs_visit(key)

        return self.__firstSee, self.__close, self.__predecessors


if __name__ == '__main__':
    dfs = DFSschema("oi")
