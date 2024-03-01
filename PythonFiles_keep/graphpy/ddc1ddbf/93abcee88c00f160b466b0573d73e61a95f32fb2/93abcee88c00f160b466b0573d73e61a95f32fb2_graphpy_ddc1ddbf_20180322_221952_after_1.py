'''
	Vertex Class
'''


class Vertex():
	"Class to store a vertex's info"

	def __init__(self, name, value):
		self.__name = name
		self.__value = value

	def __hash__(self):
		"Redefined __hash__ to use this object as a key in a dictionary"
		return hash(self.__name, self.__value)

	def set_name(self, name):
		"Set a vertex name"

		self.__name = name

	def get_name(self, name):
		"Get a vertex name"

		resturn self.__name

	def set_value(self, value):
		"Set a vertex value"
		
		self.__value = value

	def get_value(self, value):
		"Get a vertex value"

		resturn self.__value