
class KMedoids:
    def __init__(self, init_index_medoids, max_iter, tolerance):
        self.init_index_medoids = init_index_medoids
        self.max_iter = max_iter
        self.tolerance = tolerance
    
    def fit(self, data):
        # validate data
        # implement kmedoids algorithm
        # ...
        return self
    
    def predict(self, sample):
        # predict sample data (perlu ga kira2?)
        # ...
        return []

    def fit_predict(self, data):
        self.fit(data)
        # get labels from fit
        # ...
        return self
        