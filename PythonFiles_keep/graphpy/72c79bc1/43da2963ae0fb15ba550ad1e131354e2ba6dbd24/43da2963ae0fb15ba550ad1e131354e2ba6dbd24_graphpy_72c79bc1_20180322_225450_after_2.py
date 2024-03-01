'''
	Graph Class
'''

import edge

class Graph():
	"Class to store a edges's array and a vertex's dictionary"

	def __init__(self):
		self.__edges = {} # dicionario de tuplas.. (no source, no dest)
		self.__vertex = {}
	
	def add_edge(self, edge):
		self.__edges[(edge.get_source(), edge.get_destination())] = edge

	def remove_edge(self, edge):
		self.__edges.pop((edge.get_source(), edge.get_destination()))

	def add_vertex(self, vertex):
		self.__vertex[vertex] = []

	def get_edge_from_souce_destination(self, source, destination):
		"Get a edge from a source and a destination node"
		pass
