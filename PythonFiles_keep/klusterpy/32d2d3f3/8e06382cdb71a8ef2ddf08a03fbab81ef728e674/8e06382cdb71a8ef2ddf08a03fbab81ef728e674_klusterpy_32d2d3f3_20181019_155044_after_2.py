from klusterpy.metric.distance import euclidean_dist, manhattan_dist

class DBSCAN:
    def __init__(self, epsilon, min_pts, metric='euclidean'):
        self.epsilon = epsilon
        self.min_pts = min_pts
        if metric == "euclidean":
            self.__dist_func = euclidean_dist
        elif metric == "manhattan":
            self.__dist_func = manhattan_dist
        else:
            self.__dist_func = None
            raise ValueError('Distance metric must be one of ["euclidean", "manhattan"]')
    
    def fit(self, data):
        n_rows = len(data)
        self.labels = [None] * n_rows
        c = -1
        for i in range(0, n_rows):
            if self.labels[i] != None:
                continue
            neighbors = self.__find_neighbors(i, data)
            if len(neighbors) < self.min_pts:
                self.labels[i] = -1
                continue
            
            c += 1
            self.__grow_cluster(c, i, data, neighbors)
        return self
    
    def fit_predict(self, data):
        self.fit(data)
        return self.labels

    def __find_neighbors(self, index, data):
        neighbors = []
        n_rows = len(data)
        for i in range(0, n_rows):
            if self.__dist_func(data[index], data[i]) <= self.epsilon:
                neighbors.append(i)
        return neighbors

    def __grow_cluster(self, c, index, data, neighbors):
        self.labels[index] = c
        i = 0
        while i < len(neighbors):
            n = neighbors[i]
            if self.labels[n] == -1:
                self.labels[n] = c
            elif self.labels[n] == None:
                self.labels[n] = c
                neighbors_of_n = self.__find_neighbors(n, data)
                if len(neighbors_of_n) >= self.min_pts:
                    neighbors.extend(neighbors_of_n)
            i += 1

