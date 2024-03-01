
class AgglomerativeHierarchical:
    def __init__(self, n_cluster, linkage, metric):
        self.n_cluster = n_cluster
        self.linkage = linkage
        self.metric = metric
    
    def fit(self, data):
        # validate data
        # implement AgglomerativeHierarchical algorithm
        # ...
        return self
    
    def fit_predict(self, data):
        self.fit(data)
        # get labels from fit
        # ...
        return self