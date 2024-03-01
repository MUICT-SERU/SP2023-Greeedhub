# 'pip install -e .' in /path/to/project 

import unittest
import pandas as pd

from klusterpy.cluster.agglomerative import AgglomerativeClustering

class TestAgglomerative(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        data = pd.read_csv("iris.data.txt", header=None)
        del data[4]
        self.data = data

    def test_with_iris_complete(self):
        with open("labels_agglo_ncluster3_complete.txt") as f:
            lines = f.readlines()
        lines = " ".join(lines).split()
        self.test_labels = [int(n) for n in lines]

        n_clusters = 3
        linkage = "complete"
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage).fit(self.data.values.tolist())
        labels = model.labels
        self.assertEqual(len(labels), len(self.test_labels))
        dic = {}
        for i in range(len(labels)):
            x = dic.get(labels[i])
            if x == None:
                dic[labels[i]] = self.test_labels[i]

        for i in range(len(labels)):
            labels[i] = dic[labels[i]]

        self.assertEqual(labels, self.test_labels)

    def test_with_iris_average(self):
        with open("labels_agglo_ncluster3_average.txt") as f:
            lines = f.readlines()
        lines = " ".join(lines).split()
        self.test_labels = [int(n) for n in lines]

        n_clusters = 3
        linkage = "average"
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage).fit(self.data.values.tolist())
        labels = model.labels
        self.assertEqual(len(labels), len(self.test_labels))
        dic = {}
        for i in range(len(labels)):
            x = dic.get(labels[i])
            if x == None:
                dic[labels[i]] = self.test_labels[i]

        for i in range(len(labels)):
            labels[i] = dic[labels[i]]

        self.assertEqual(labels, self.test_labels)

if __name__ == '__main__':
    unittest.main()