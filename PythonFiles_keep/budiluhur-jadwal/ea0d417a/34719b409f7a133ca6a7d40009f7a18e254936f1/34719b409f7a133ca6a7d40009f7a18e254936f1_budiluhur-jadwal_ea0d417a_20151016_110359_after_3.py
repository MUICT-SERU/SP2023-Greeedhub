from budiluhur.jadwal import fakultas
from pprint import pprint

# inisialisasi class Fakultas
f = fakultas.Fakultas()
kode_fakultas = f.get_all()
fakultas_teknik_informatika = f.get_kode_fakultas()
pprint(fakultas_teknik_informatika)
