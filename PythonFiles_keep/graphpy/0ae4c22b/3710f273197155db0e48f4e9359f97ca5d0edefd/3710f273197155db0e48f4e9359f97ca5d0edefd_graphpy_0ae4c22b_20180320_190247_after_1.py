'''
	Edge Class
'''


class Edge():
	"Class to store a edges's info"

	def __init__(self, name, value, source, destination):
		self.name = name
		self.value = value
		self.source = source
		self.destination = destination
