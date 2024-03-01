import abc
import sys
import six

@six.add_metaclass(abc.ABCMeta)
class SearchStrategy(object):
    def setup(self, adjacent_list):
        self.__adjacent_list = adjacent_list

    @abc.abstractmethod
    def search(self, initial_vertex):
        return

    def get_adjacent_list(self):
        return self.__adjacent_list