# 'pip install -e .' in /path/to/project 

import unittest
import pandas as pd

from klusterpy.cluster.dbscan import DBSCAN

class TestDBSCAN(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        data = pd.read_csv("iris.data.txt", header=None)
        del data[4]
        self.data = data
        
        with open("labels_dbscan_eps0.42_minpts5_eu.txt") as f:
            lines = f.readlines()
        lines = " ".join(lines).split()
        self.test_labels = [int(n) for n in lines]

    def test_with_iris(self):
        epsilon = 0.42
        min_pts = 5
        model = DBSCAN(epsilon=epsilon, min_pts=min_pts).fit(self.data.values)
        labels = model.labels
        self.assertEqual(labels, self.test_labels)

if __name__ == '__main__':
    unittest.main()