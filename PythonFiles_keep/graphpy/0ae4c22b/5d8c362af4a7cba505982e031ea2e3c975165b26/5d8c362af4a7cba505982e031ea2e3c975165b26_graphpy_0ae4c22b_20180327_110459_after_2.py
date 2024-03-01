'''
	Graph Class
'''

class Graph(object):
	"Class to store a edges's array and a vertex's dictionary"

	def __init__(self):
		self.__edges = {} # dicionario de tuplas.. (no source, no dest)
		self.__adjacent_list = {}

	def add_edge(self, edge, directed=False):
		"Add a new edge to the graph"

		# insert source
		if edge.get_source() not in self.__adjacent_list:
			self.__adjacent_list[edge.get_source()] = []
		# insert destination
		if edge.get_destination() not in self.__adjacent_list:
			self.__adjacent_list[edge.get_destination()] = []

		# insert edge and update adjacent list
		self.__edges[(edge.get_source(), edge.get_destination())] = edge
		self.__adjacent_list[edge.get_source()].append(edge.get_destination())

		# if not directed.. do the same with the other node
		if not directed:
			self.__edges[(edge.get_destination(), edge.get_source())] = edge
			self.__adjacent_list[edge.get_destination()].append(edge.get_source())

	def remove_edge(self, edge_to_remove):
		"Remove a edge from the graph"

		# Remove vertex from the adjacent_list
		self.__edges.pop((edge_to_remove.get_source(), edge_to_remove.get_destination()))

	def add_vertex(self, new_vertex):
		"Add a new vertex to the graph"

		self.__adjacent_list[new_vertex] = []

	# Remove vertex from the adjacent_list (remove from edge list to)

	def get_edge_from_souce_destination(self, source, destination):
		"Get a edge from a source and a destination node"
		pass

	def print_adjacent_list(self):
		"Print the adjacent list"

		print(self.__adjacent_list)
