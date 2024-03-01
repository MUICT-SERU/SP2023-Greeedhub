import struct
import packet

class Packet19Parser(object):

	def parse(self, world, player, data):
		if data[1] != player.playerID:
			print data[6:]


class Packet19(packet.Packet):

	def __init__(self,  player, msg=":)"):
		super(Packet19, self).__init__(0x19)
		self.addData(chr(player.playerID))
		self.addData(chr(1))
		self.addData(chr(1))
		self.addData(chr(1))
		self.addData(msg, pascalString=True)

