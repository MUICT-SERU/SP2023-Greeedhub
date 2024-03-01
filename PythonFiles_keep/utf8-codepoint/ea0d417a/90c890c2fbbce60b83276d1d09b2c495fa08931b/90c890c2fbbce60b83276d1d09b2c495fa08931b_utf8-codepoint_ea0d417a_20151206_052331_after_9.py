# Program sederhana untuk konversi 
# karakter UTF-8 ke representasi hexadesimal
# --------------------------------------------
# _Yanwar Solahudin work in 5 Dec, 2015 22:32

class CodePoint(object):
	
	def __init__(self, str_utf8):
		# variabel private untuk menyimpan 
		# nilai yang di masukan oleh user.
		self.__str_utf8 = str_utf8.replace("U+", "0x")
		self.__int_repr = 0
		self.__code_points = {}
		self.__code_point = 0
		self.__bit_repr = ""
		self.__len_bit = 0
		self.__initial_bit = ""
		self.__further_bit = "10"
		self.__slice_bytes = []
		self.utf8 = {}
		self.__result_bit = []
		self.__result_hex = []
		self.__result_int = []
		self.__result_code = self.__str_utf8
		self.__result_all = {}
		
		
		self.__initialize()
	
	def __initialize(self):
		self.__set_code_points()
		self.__character_validator(self.__str_utf8)
		self.__change_data_input()
		self.__get_code_point()
		self.__get_code_point()
		self.__process()
		
	def __set_code_points(self):
		# ------------------------------------------------
		# menyiapkan dictionary untuk code points,
		# untuk lebih jelas lagi, lihat aturan code points
		# pada tabel skema UTF-8 di wikipedia.
		# ------------------------------------------------
		self.__code_points = {
			# aturan untuk bit code point 7
			# byte dalam sequence-nya 1 (8bit).
			"P1": (int(0X0000), int(0X007F), 7),
			# aturan untuk bit code point 11
			# byte dalam sequence-nya 2 (16bit).
			"P2": (int(0X0080), int(0X07FF), 11),
			# aturan untuk bit code point 16
			# byte dalam sequence-nya 3 (24bit)
			"P3": (int(0X0800), int(0XFFFF), 16),
			# aturan untuk bit code point 21
			# byte dalam sequence-nya 4 (32bit)
			"P4": (int(0X10000), int(0X1FFFFF), 21),
			# aturan untuk bit code point 26
			# byte dalam sequence-nya 5 (40bit)
			"P5": (int(0X200000), int(0X3FFFFFF), 26),
			# aturan untuk bit code point 31
			# byte dalam sequence-nya 6 (48bit)
			"P6": (int(0X4000000), int(0X7FFFFFFF), 31),
		}
		
	
	def __character_validator(self, data):
		# --------------------------------------------
		# validasi data, jika data merupakan
		# objek atau instance bukan dari class string.
		# --------------------------------------------
		if not isinstance(data, str):
			raise("harus string")
			
	
	def __change_data_input(self):
		# --------------------------------------------------------
		# merubah unicode code point (U+20AC) menjadi integer
		# yang hasilnya akan diassign ke variabel self.__int_repr.
		# --------------------------------------------------------
		self.__int_repr = ord(chr(int(self.__str_utf8, 16)))
		
		# ----------------------------------------------------------
		# nerubah integer unicode ke dalam bentuk representasi biner
		# yang hasilnya akan diassign ke variabel self.__bit_repr.
		# ----------------------------------------------------------
		self.__bit_repr = bin(self.__int_repr).replace("0b", "")
		
		# -----------------------------------
		# mendapatkan panjang biner saat ini.
		# -----------------------------------
		self.__bit_len = len(self.__bit_repr)
		
	def __get_code_point(self):
		# untuk nilai int dari karakter di bit code point 7.
		p10 = self.__int_repr >= self.__code_points["P1"][0]
		p11 = self.__int_repr <= self.__code_points["P1"][1]
		
		# untuk nilai int dari karakter di bit code point 11
		p20 = self.__int_repr >= self.__code_points["P2"][0]
		p21 = self.__int_repr <= self.__code_points["P2"][1]
		
		# untuk nilai int dari karakter di bit code point 16
		p30 = self.__int_repr >= self.__code_points["P3"][0]
		p31 = self.__int_repr <= self.__code_points["P3"][1]
		
		# untuk nilai int dari karakter di bit code point 21
		p40 = self.__int_repr >= self.__code_points["P4"][0]
		p41 = self.__int_repr <= self.__code_points["P4"][1]
		
		# untuk nilai int dari karakter di bit code point 26
		p50 = self.__int_repr >= self.__code_points["P5"][0]
		p51 = self.__int_repr <= self.__code_points["P5"][1]
		
		# untuk nilai int dari karakter di bit code point 31
		p60 = self.__int_repr >= self.__code_points["P6"][0]
		p61 = self.__int_repr <= self.__code_points["P6"][1]
		
		# start pengecekan
		if  p11 and p10:
			# jika nilai biner ada di kisaran bit code point 7.
			self.__code_point = self.__code_points["P1"][2]
			# set pengkodean 1 bit, nilai 0 sebanyak 1 kali.
			self.__initial_bit = "0"
		elif p21 and p20:
			# jika nilai biner ada di kisaran bit code point 11.
			self.__code_point = self.__code_points["P2"][2]
			# set pengkodean 2 bit, nilai 1 sebanyak 2 kali,
			# nilai 0 sebanyak 1 kali.
			self.__initial_bit = "110"
		elif p31 and p30:
			# jika nilai biner ada di kisaran bit code point 16.
			self.__code_point = self.__code_points["P3"][2]
			# set pengkodean 3 bit, nilai 1 sebanyak 3 kali,
			# nilai 0 sebanyak 1 kali.
			self.__initial_bit = "1110"
		elif p41 and p40:
			# jika nilai biner ada di kisaran bit code point 21.
			self.__code_point = self.__code_points["P4"][2]
			# set pengkodean 4 bit, nilai 1 sebanyak 4 kali,
			# nilai 0 sebanyak 1 kali.
			self.__initial_bit = "11110"
		elif p51 and p50:
			self.__code_point = self.__code_points["P5"][2]
			# set pengkodean 5 bit, nilai 1 sebanyak 5 kali,
			# nilai 0 sebanyak 1 kali.
			self.__initial_bit = "111110"
		elif p61 and p60:
			self.__code_point = self.__code_points["P6"][2]
			# set pengkodean 6 bit, nilai 1 sebanyak 6 kali,
			# nilai 0 sebanyak 1 kali.
			self.__initial_bit = "1111110"
		else:
			raise("nilai tidak ada di dalam daftar range skema utf-8")
			
	
	def __process(self):
		# gandakan 0 sebanyak selisih jumlah code point dan
		# panjang bit.
		zero_padd = "0" * (self.__code_point - len(self.__bit_repr))
		# gabungkan inisial bit yang di dapat dari hasil pengecekan
		# pada code point.
		self.__bit_repr = self.__initial_bit + zero_padd + self.__bit_repr
		
		# ambil sisa bit mulai dari bit ke 9 sampai akhir.
		self.__slice_bytes = self.__bit_repr[8:]
		# set bagian
		n = 6
		# set sisa bit
		line = self.__slice_bytes
		# pecah menjadi beberapa bagian, dimana
		# setiap bagian berisi 6bit, lalu concate dengan 
		# bit kelanjutan (10).
		self.__slice_bytes = [
			"10" + i for i in [
						line[i:i+n] for i in range(0, len(line), n)
					]
		]
		# masukan semua bit yang tersisa untuk akhir proses.
		self.__bit_repr = self.__bit_repr[:8] + "".join(self.__slice_bytes)
		
		
	def to_string(self):
		n = 8
		line = self.__bit_repr
		return " ".join([line[i:i+n] for i in range(0, len(line), n)])
		
	def to_list(self):
		n = 8
		line = self.__bit_repr
		result = [line[i:i+n] for i in range(0, len(line), n)]
		return result
		
	def to_hex(self):
		hex_val = []
		n = 8
		line = self.__bit_repr
		data = [line[i:i+n] for i in range(0, len(line), n)]
		for i in data:
			d = hex(int(i, 2))
			hex_val.append(d.replace("0x","").upper())
		return " ".join(hex_val)
	
	def to_int(self):
		int_val = []
		n = 8
		line = self.__bit_repr
		data = [line[i:i+n] for i in range(0, len(line), n)]
		for i in data:
			d = int(i, 2)
			int_val.append(str(d))
		return " ".join(int_val)

	def get_all(self, format_json=False):
		self.__result_int = []
		self.__result_hex = []
		self.__result_bit = []
		n = 8
		line = self.__bit_repr
		data = [line[i:i+n] for i in range(0, len(line), n)]
		for i in data:
			d = int(i, 2)
			self.__result_int.append(d)
			d = hex(int(i, 2))
			self.__result_hex.append(d)
			self.__result_bit.append(i)
		
		data_results = {
			self.__result_code: {
				"code_point": self.__code_point,
				"initial_bit": self.__initial_bit,
				"integer_list": self.__result_int,
				"hexa_list": self.__result_hex,
				"bit_list": self.__result_bit,
			}
		}
		
		if format_json:
			import json
			return json.dumps(data_results, ensure_ascii=False)
		return data_results
	
	def bprint(self):
		import pprint as pp
		pp.pprint(self.get_all())
		
if __name__ == '__main__':
	utf8 = CodePoint("U+0024")
	print(utf8.to_string())
	print(utf8.to_hex())	
	print(utf8.to_int())
	print(utf8.get_all(True))
	utf8.bprint()
	
	
		
