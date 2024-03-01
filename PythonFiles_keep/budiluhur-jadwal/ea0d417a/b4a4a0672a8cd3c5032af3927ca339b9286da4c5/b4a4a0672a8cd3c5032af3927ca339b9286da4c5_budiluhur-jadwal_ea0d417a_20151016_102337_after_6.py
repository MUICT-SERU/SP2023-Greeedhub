from budiluhur.jadwal.fakultas import Fakultas
import pprint

'''
f = Fakultas()
print(f.get_fakultas('01'))
jadwal = f.jadwal_instance()
#print(f.jadwal_instance().to_json())
#pprint.pprint(jadwal.get_from_dosen('Agung Saputra, S.Kom, M.M'))
pprint.pprint(jadwal.get_from_ruangan('-'))
print(jadwal.data_json)
'''

f = Fakultas()
f.get_fakultas('01')
#pprint.pprint(f.get_all())
jadwal = f.jadwal_instance()
#pprint.pprint(jadwal.get_all())
pprint.pprint(jadwal.filter_kehadiran())
