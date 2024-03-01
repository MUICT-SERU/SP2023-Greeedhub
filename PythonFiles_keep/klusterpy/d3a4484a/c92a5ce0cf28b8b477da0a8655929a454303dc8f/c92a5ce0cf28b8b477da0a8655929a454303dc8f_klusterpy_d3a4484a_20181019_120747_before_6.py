# buat ngecoba2 kodenya ud bener/belum

# run 'pip install -e .' in /path/to/project dir (contains setup.py) to install in develop mode
# run above command again if you made changes in the library
# after fully done, don't forget to run 'pip uninstall klusterpy' to remove local klusterpy

# gmn caranya supaya bisa jadi gini ya:
# from klusterpy.cluster import AgglomerativeHierarchical, DBSCAN, KMeans, KMedoids
from klusterpy.cluster.DBSCAN import DBSCAN
import numpy as np

X = np.array([[1, 2], [2, 2], [2, 3], [8, 7], [8, 8], [25, 80]])
dbscan = DBSCAN(epsilon=3, min_pts=2).fit(X)
