'''
	Edge Class
'''


class Edge():
	"Class to store a edges's info"

	def __init__(self, label, value, source, destination):
		self.__label = label
		self.__value = value
		self.__source = source
		self.__destination = destination

	def set_label(self, label):
		"Set a edge label"

		self.__label = label
