from math import sqrt

def euclidean_dist(a, b):
	dist = 0
	for i in range(len(a)):
		dist += (a[i]-b[i])*(a[i]-b[i])
	
	return sqrt(dist)

def manhattan_dist(x, y):
    return 0