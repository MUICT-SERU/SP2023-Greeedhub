import numpy as np
import random

class KMedoids:
    def __init__(self, n_cluster, max_iter=300, tolerance=0.001, init='kmeans++'):
        self.n_cluster = n_cluster
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.init = init

        if isinstance(init, list):
            self.medoids = init
        self.clusters = {}
        self.curr_distance = 0

        self.__data = None
        self.__rows = 0
        self.__columns = 0
        self.cluster_distances = {}
    
    def fit(self, data):
        self.__data = data
        self.__set_data()
        self.__kmedoids_run()
        return self

    def __kmedoids_run(self):
        if isinstance(self.init, str):
            if self.init == 'kmeans++':
                self.__initialize_medoids()
        self.clusters, self.cluster_distances = self.__calculate_clusters(self.medoids)
        self.__update_clusters()

    def __update_clusters(self):
        for i in range(self.max_iter):
            cluster_distance_to_new_medoids = self.__swap_and_recalculate_clusters()
            if self.__is_new_cluster_dist_small(cluster_distance_to_new_medoids) == True:
                self.clusters, self.cluster_distances = self.__calculate_clusters(self.medoids)
            else:
                break

    def __is_new_cluster_dist_small(self, cluster_distance_to_new_medoids):
        existance_dist = self.calculate_distance_of_clusters()
        new_dist = self.calculate_distance_of_clusters(cluster_distance_to_new_medoids)

        if existance_dist > new_dist and (existance_dist - new_dist) > self.tolerance:
            self.medoids = cluster_distance_to_new_medoids.keys()
            return True
        return False

    def calculate_distance_of_clusters(self, cluster_dist = None):
        if cluster_dist == None:
            cluster_dist = self.cluster_distances
        dist = 0
        for medoid in cluster_dist.keys():
            dist += cluster_dist[medoid]
        return dist

    def __swap_and_recalculate_clusters(self):
        cluster_dist = {}
        for medoid in self.medoids:
            is_shortest_medoid_found = False
            for data_index in self.clusters[medoid]:
                if data_index != medoid:
                    cluster_list = list(self.clusters[medoid])
                    cluster_list[self.clusters[medoid].index(data_index)] = medoid
                    new_distance = self.calculate_inter_cluster_distance(data_index, cluster_list)
                    if new_distance < self.cluster_distances[medoid]:
                        cluster_dist[data_index] = new_distance
                        is_shortest_medoid_found = True
                        break
            if is_shortest_medoid_found == False:
                cluster_dist[medoid] = self.cluster_distances[medoid]
        return cluster_dist

    def calculate_inter_cluster_distance(self, medoid, cluster_list):
        distance = 0
        for data_index in cluster_list:
            distance += self.__get_distance(medoid, data_index)
        return distance/len(cluster_list)

    def __calculate_clusters(self, medoids):
        clusters = {}
        cluster_distances = {}
        for medoid in medoids:
            clusters[medoid] = []
            cluster_distances[medoid] = 0
        for row in range(self.__rows):
            nearest_medoid, nearest_distance = self.__get_shortest_distance_to_medoid(row, medoids)
            cluster_distances[nearest_medoid] += nearest_distance
            clusters[nearest_medoid].append(row)
        for medoid in medoids:
            cluster_distances[medoid] /= len(clusters[medoid])
        return clusters, cluster_distances

    def __get_shortest_distance_to_medoid(self, row_idx, medoids):
        min_dist = float('inf')
        curr_medoid = None
        for medoid in medoids:
            curr_distance = self.__get_distance(medoid, row_idx)
            if curr_distance < min_dist:
                min_dist = curr_distance
                curr_medoid = medoid
        return curr_medoid, min_dist

    def __initialize_medoids(self):
        self.medoids.append(random.randint(0, self.__rows-1))
        while len(self.medoids) != self.n_cluster:
            self.medoids.append(self.__find_distant_medoid())

    def __find_distant_medoid(self):
        distances = []
        indices = []
        for row in range(self.__rows):
            indices.append(row)
            distances.append(self.__get_shortest_distance_to_medoid(row, self.medoids)[1])
        distances_idx = np.argsort(distances)
        choosen_dist = self.__select_distant_medoid(distances_idx)
        return indices[choosen_dist]

    def __select_distant_medoid(self, distances_idx):
        start_idx = len(distances_idx)
        end_idx = len(distances_idx) - 1
        return distances_idx[random.randint(start_idx, end_idx)]

    def __get_distance(self, x1, x2):
        a = np.array(self.__data[x1])
        b = np.array(self.__data[x2])
        return np.linalg.norm(a-b)

    def __set_data(self):
        self.__rows = len(self.__data)
        self.__columns = len(self.__data[0])

    def get_clusters(self):
        return self.clusters
    
    def data_clusters_to_labels(self, cluster_idxs):
        cluster_idxs = [v for _, v in cluster_idxs.items()]
        size = 0
        for i in range(0, len(cluster_idxs)):
            size += len(cluster_idxs[i])
        labels = [0] * size
        for i in range(0, len(cluster_idxs)):
            for j in range(0, len(cluster_idxs[i])):
                labels[cluster_idxs[i][j]] = i
        return labels

    def fit_predict(self, data):
        self.fit(data)
        return self.data_clusters_to_labels(self.get_clusters())
        