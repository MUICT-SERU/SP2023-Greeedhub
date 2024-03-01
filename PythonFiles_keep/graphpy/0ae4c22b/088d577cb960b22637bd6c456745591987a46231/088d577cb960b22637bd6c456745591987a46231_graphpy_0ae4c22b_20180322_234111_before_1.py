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

	def get_label(self):
		"Get a edge label"

		return self.__label

	def set_value(self, value):
		"Set a edge value"

		self.__value = value

	def get_value(self):
		"Get a edge value"

		return self.__value

	def set_source(self, source):
		"Set a edge source"

		self.__source = source

	def get_source(self):
		"Get a edge source"

		return self.__source

	def set_destination(self, destination):
		"Set a edge destination"

		self.__destination = destination

	def get_destination(self):
		"Get a edge destination"

		return self.__destination
