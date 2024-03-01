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
