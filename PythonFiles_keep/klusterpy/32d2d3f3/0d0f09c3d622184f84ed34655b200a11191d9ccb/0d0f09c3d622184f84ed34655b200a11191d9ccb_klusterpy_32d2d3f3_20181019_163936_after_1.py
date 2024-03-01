from klusterpy.metric.distance import euclidean_dist, manhattan_dist

class AgglomerativeClustering:
    def __init__(self, n_clusters=2, linkage="single", metric="euclidean"):
        self.n_clusters = n_clusters
        self.labels = []

        if linkage == "single":
            self.__linkage_func = self.__single_dist
        elif linkage == "complete":
            self.__linkage_func = self.__complete_dist
        elif linkage == "average":
            self.__linkage_func = self.__average_dist
        elif linkage == "average group":
            self.__linkage_func = self.__average_dist
        else:
            raise ValueError('Linkage must be one of ["single", "complete", "average", "average group"]')

        if metric == "euclidean":
            self.__dist_func = euclidean_dist
        elif metric == "manhattan":
            self.__dist_func = manhattan_dist
        else:
            self.__dist_func = None
            raise ValueError('Distance metric must be one of ["euclidean", "manhattan"]')

    def __single_dist(self, c1, c2):
        dist = -1
        for a in c1:
            for b in c2:
                tmpdist = euclidean_dist(a, b)
                if dist < 0 or tmpdist < dist:
                    dist = tmpdist

        return dist

    def __complete_dist(self, c1, c2):
        dist = -1
        for a in c1:
            for b in c2:
                tmpdist = euclidean_dist(a, b)
                if dist < 0 or tmpdist > dist:
                    dist = tmpdist

        return dist

    def __average_dist(self, c1, c2):
        dist = 0
        for a in c1:
            for b in c2:
                tmpdist = euclidean_dist(a, b)
                dist += tmpdist

        return dist / (len(c1) * len(c2))

    def __average_group_dist(self, c1, c2):
        avr_1 = [0 for _ in range(len(c1[0][0]))]
        avr_2 = [0 for _ in range(len(c2[0][0]))]
        for i in range(len(c1)):
            for j in range(len(c1[i])):
                avr_1[j] += c1[i][j]
                avr_2[j] += c2[i][j]

        for i in range(len(avr_1)):
            avr_1[i] /= len(avr_1)
            avr_2[i] /= len(avr_2)

        return euclidean_dist(avr_1, avr_2)
    
    def fit(self, data):
        n = len(data)
        cluster = [[d] for d in data]
        index = [[i] for i in range(n)]
        self.labels = [i for i in range(n)]

        for _ in range(n - self.n_clusters):
            now_i = -1
            now_j = -1
            dist = -1.
            for i in range(len(cluster)):
                for j in range(len(cluster) - i - 1):
                    tmpdist = self.__linkage_func(cluster[i], cluster[i + j + 1])
                    if dist < 0 or tmpdist < dist:
                        dist = tmpdist
                        now_j = i + j + 1
                        now_i = i

            cluster[now_i] = cluster[now_i] + cluster[now_j]
            index[now_i] = index[now_i] + index[now_j]
            for i in range(len(cluster[now_j])):
                self.labels[index[now_j][i]] = self.labels[index[now_i][0]]
            del cluster[now_j]
            del index[now_j]

        exist = [False for _ in range(self.n_clusters)]
        for label in self.labels:
            if label < self.n_clusters:
                exist[label] = True

        now = 0
        dic = {}
        for i in range(n):
            label = self.labels[i]
            if label >= self.n_clusters:
                x = dic.get(label)
                if x == None:
                    while exist[now]:
                        now += 1
                    dic[label] = now
                    self.labels[i] = now
                    now += 1
                else:
                    self.labels[i] = x

        return self
    
    def fit_predict(self, data):
        self.fit(data)
        return self.labels