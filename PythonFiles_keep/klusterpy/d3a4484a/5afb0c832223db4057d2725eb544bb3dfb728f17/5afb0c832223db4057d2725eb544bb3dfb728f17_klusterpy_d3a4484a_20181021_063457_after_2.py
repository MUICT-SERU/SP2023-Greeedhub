import unittest
import numpy as np
import pandas as pd

from klusterpy.cluster.kmeans import KMeans
from sklearn.cluster import KMeans as SK_KMeans

class TestKMeans(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        data = pd.read_csv("iris.data.txt", header=None)
        del data[4]
        self.data = data

        with open("labels_kmeans_nclust3.txt") as f:
            lines = f.readlines()
        lines = " ".join(lines).split()

        self.test_labels = [int(n) for n in lines]
        self.n_cluster = 3
        self.init = np.array([self.data.values[24], self.data.values[74], self.data.values[124]], np.float64)
        self.n_init = 10

    def test_fit_predict(self):
        labels = KMeans(n_clusters=self.n_cluster, init=self.init).fit_predict(self.data.values)
        self.assertEqual(labels, self.test_labels)
    
    def test_predict(self):
        model = KMeans(n_clusters=self.n_cluster, init=self.init).fit(self.data.values)
        self.assertEqual(model.predict(self.init), [0, 1, 2])

if __name__ == '__main__':
    unittest.main()