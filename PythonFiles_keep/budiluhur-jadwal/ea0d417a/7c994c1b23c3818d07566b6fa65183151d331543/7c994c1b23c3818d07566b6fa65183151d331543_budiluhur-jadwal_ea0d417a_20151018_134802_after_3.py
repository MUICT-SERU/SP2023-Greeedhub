from budiluhur.jadwal import fakultas
from pprint import pprint

# inisialisasi class Fakultas
fak = fakultas.Fakultas()
# id fakultas bisa diperoleh di fak.get_all()
fe = fak.get_fakultas('03', True) # Fakultas Ekonomi
# fe.jadwal.clean_dot()

pprint(fe.jadwal.get_from_ruangan('4.3.3'))
