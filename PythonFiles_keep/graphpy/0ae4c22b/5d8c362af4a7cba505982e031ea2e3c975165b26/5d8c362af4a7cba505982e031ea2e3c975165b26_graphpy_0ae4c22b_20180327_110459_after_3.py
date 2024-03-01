'''
	Vertex Class
'''


class Vertex(object):
	"Class to store a vertex's info"

	def __init__(self, name, value=None):
		self.__name = name
		self.__value = value

	def __hash__(self):
		"Redefined __hash__ to use this object as a key in a dictionary"

		return hash(self.__name)

	def __str__(self):
		"Value to use when call the function print"

		return self.__name

	def __repr__(self):
		"Value to use when use repr()"

		return self.__name

	def set_name(self, name):
		"Set a vertex name"

		self.__name = name

	def get_name(self):
		"Get a vertex name"

		return self.__name

	def set_value(self, value):
		"Set a vertex value"

		self.__value = value

	def get_value(self):
		"Get a vertex value"

		return self.__value
