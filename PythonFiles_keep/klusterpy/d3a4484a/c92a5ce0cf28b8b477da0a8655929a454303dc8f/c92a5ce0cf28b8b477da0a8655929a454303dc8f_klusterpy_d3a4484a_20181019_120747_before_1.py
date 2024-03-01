
class DBSCAN:
    def __init__(self, epsilon, min_pts, metric='euclidean'):
        self.epsilon = epsilon
        self.min_pts = min_pts
        self.metric = metric
    
    def fit(self, data):
        # validate data
        # implement dbscan algorithm
        # ...
        return self
    
    def fit_predict(self, data):
        self.fit(data)
        # get labels from fit
        # ...
        return self