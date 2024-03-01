import unittest
import numpy as np
import pandas as pd

from klusterpy.cluster.kmedoids import KMedoids
from pyclustering.cluster.kmedoids import kmedoids

class TestKMedoids(unittest.TestCase):

  @classmethod
  def setUpClass(self):
        data = pd.read_csv("iris.data.txt", header=None)
        del data[4]
        self.data = data

        with open("labels_kmedoids.txt") as f:
            lines = f.readlines()
        lines = " ".join(lines).split()

        self.test_labels = [int(n) for n in lines]
        self.n_cluster = 3
        self.init = [25, 75, 125]
        self.n_init = 10

  def test_fit_predict(self):
        labels = KMedoids(n_cluster=self.n_cluster, init=self.init).fit_predict(self.data.values)
        print(labels)
        self.assertEqual(labels, self.test_labels)

if __name__ == '__main__':
    unittest.main()