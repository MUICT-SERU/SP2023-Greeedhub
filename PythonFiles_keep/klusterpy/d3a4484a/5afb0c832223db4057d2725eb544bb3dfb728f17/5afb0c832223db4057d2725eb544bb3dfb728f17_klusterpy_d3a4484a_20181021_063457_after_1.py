from klusterpy.metric.distance import euclidean_dist

import numpy as np
import math, random

class KMeans:
    def __init__(self, n_clusters=2, init='random', max_iter=300, tolerance=0.0001):
        self.n_clusters = n_clusters
        self.init = init
        if isinstance(init, np.ndarray):
            self.centroids = init
        self.max_iter = max_iter
        self.tolerance = tolerance
    
    def fit(self, data):
        if isinstance(self.init, str):
            if self.init == 'k-means++':
                self.__init_kmeans_plus2(data)
            elif self.init == 'random':
                self.__init_random(data)
            else:
                raise ValueError('Init must be one of ["k-means++", "random"] or an ndarray')
        self.labels = [None] * len(data)
        
        iteration_count = 1
        self.__assignment_clustering(data)
        error = self.__square_error(data)
        while iteration_count <= self.max_iter:
            iteration_count += 1
            self.__recalculate_centroids(data)
            self.__assignment_clustering(data)
            new_error = self.__square_error(data)
            if math.fabs(error - new_error) <= self.tolerance:
                error = new_error
                break
            error = new_error
        self.n_iter = iteration_count
        self.error = error
        return self
    
    def predict(self, samples):
        predictions = []
        for sample in samples:
            predictions.append(self.__assign_to_cluster(sample))
        return predictions

    def fit_predict(self, data):
        self.fit(data)
        return self.labels

    def __init_random(self, data):
        self.centroids = random.sample(range(len(data)), self.n_clusters)
        return self

    def __init_kmeans_plus2(self, data):
        # not implemented yet
        raise NotImplementedError('__init_kmeans_plus2')
        return self

    def __assignment_clustering(self, data):
        n_rows = len(data)
        self.labels = [self.__assign_to_cluster(data[i]) for i in range(n_rows)]
        self.clusters = [[j for j, x in enumerate(self.labels) if x == i] for i in range(self.n_clusters)]
        return self

    def __assign_to_cluster(self, row):
        min_c = 0
        min_dist = euclidean_dist(row, self.centroids[min_c])
        for c in range(min_c+1, self.n_clusters):
            dist = euclidean_dist(row, self.centroids[c])
            if dist < min_dist:
                min_dist, min_c = dist, c
        return min_c
    
    def __recalculate_centroids(self, data):
        for c, indexes in enumerate(self.clusters):
            sum_point = [0] * len(data[len(data) - 1])
            for index in indexes:
                for i, col in enumerate(data[index]):
                    sum_point[i] += col
            c_size = len(indexes)
            self.centroids[c] = [x/c_size for x in sum_point]
        return self

    def __square_error(self, data):
        square_error = 0
        for i, label in enumerate(self.labels):
            square_error += euclidean_dist(data[i], self.centroids[label])
        return square_error
        