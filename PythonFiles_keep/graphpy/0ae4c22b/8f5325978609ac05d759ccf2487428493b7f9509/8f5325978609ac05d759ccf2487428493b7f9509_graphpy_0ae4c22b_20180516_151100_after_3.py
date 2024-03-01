def get_min(nodes, distance):
    min = nodes[0]
    # print(distance)
    for node in nodes:
        if distance[min] > distance[node]:
            min = node
    nodes.remove(min)
    return min
