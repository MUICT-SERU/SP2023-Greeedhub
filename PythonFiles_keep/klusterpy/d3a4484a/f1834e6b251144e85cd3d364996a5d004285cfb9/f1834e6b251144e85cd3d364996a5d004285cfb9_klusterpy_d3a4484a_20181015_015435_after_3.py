
class KMeans:
    def __init__(self, n_cluster, max_iter, tolerance):
        self.n_cluster = n_cluster
        self.max_iter = max_iter
        self.tolerance = tolerance
    
    def fit(self, data):
        # validate data
        # implement kmeans algorithm
        # ...
        return self
    
    def predict(self, sample):
        # predict sample data
        # ...
        return []

    def fit_predict(self, data):
        self.fit(data)
        # get labels from fit
        # ...
        return self
        