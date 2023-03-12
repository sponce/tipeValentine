import tsplib95

# extract problem with tsplib
problemfile = 'ch130.tsp'
problem = tsplib95.load(problemfile)
nodes = list(problem.get_nodes())
nodeToIndex = {nodes[i]:i for i in range(len(nodes))}

# clusterize route
import math
NX = 4
NY = 3
maxX = max([pos[0] for name, pos in problem.node_coords.items()])+1
maxY = max([pos[1] for name, pos in problem.node_coords.items()])+1
clusters = [[] for n in range(NX*NY)]
nodeToCluster = {}
for n in nodes:
    x,y = problem.node_coords[n]
    nx = math.trunc(NX*x/maxX)
    ny = math.trunc(NY*y/maxY)
    cluster = ny*NX+nx
    clusters[cluster].append(n)
    nodeToCluster[n] = cluster

# plot nodes with matplotlib and networkx
import matplotlib.pyplot as plt
import networkx as nx

colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
G = problem.get_graph()
for n in range(len(clusters)):
    cluster = clusters[n]
    nx.draw_networkx_nodes(G, problem.node_coords, cluster, node_size=20, node_color=colors[n%len(colors)]);

# create new graph with clusters (5.2.2 of the thesis)
INFINITE = 9999999999999999
from python_tsp.distances import tsplib_distance_matrix
import numpy as np
Gdistance_matrix = tsplib_distance_matrix(problemfile)
Hdistance_matrix = np.full_like(Gdistance_matrix, INFINITE)
P2 = 8000*NX*NY # sth > min Tour len * nb subclusters
H = nx.Graph()
# same nodes
for node in nodes: H.add_node(node)
# 0 weight in each subcluster cycle
for cluster in clusters:
    for i in range(1, len(cluster)):
        H.add_edge(cluster[i-1], cluster[i], weight=0)
        Hdistance_matrix[nodeToIndex[cluster[i-1]]][nodeToIndex[cluster[i]]] = 0
    H.add_edge(cluster[-1], cluster[0], weight=0)
    Hdistance_matrix[nodeToIndex[cluster[-1]]][nodeToIndex[cluster[0]]] = 0
# edges from subcluster to other subclusters
for a in range(len(clusters)):
    for b in range(len(clusters)):
        if a == b: break
        for i1 in range(len(clusters[a])):
            n1 = clusters[a][i1]
            nindex1 = nodeToIndex[n1]
            np1 = clusters[a][i1] if i1 > 0 else clusters[a][-1]
            for n2 in clusters[b]:
                nindex2 = nodeToIndex[n2]
                w = Gdistance_matrix[nindex1][nindex2]+P2
                H.add_edge(n1, n2, weight=w)
                Hdistance_matrix[nindex1][nindex2] = w

#nx.draw_networkx_edges(H, problem.node_coords, node_size=0, width=1)
#plt.show()

# compute best route in H
from python_tsp.heuristics import solve_tsp_simulated_annealing
permutation, distance = solve_tsp_simulated_annealing(Hdistance_matrix)

route = list(nx.utils.pairwise([nodes[p] for p in permutation]))
route.append((route[-1][1],route[0][0])) # close route
nx.draw_networkx_edges(H, problem.node_coords, route, node_size=0, width=1)
plt.show()

# convert back to best route in G
firstNode = nodes[permutation[0]]
route = [firstNode,]
lastclus = nodeToCluster[firstNode]
for v in [nodes[p] for p in permutation[1:]]:
    clus = nodeToCluster[v]
    if lastclus != clus:
        route.append(v)
        lastclus = clus
distance = distance - P2*len(clusters)
print(distance)

# create closed route in nx format
route = list(nx.utils.pairwise(route))
route.append((route[-1][1],route[0][0])) # close route

# display route
nx.draw_networkx_edges(G, problem.node_coords, route, node_size=0, width=1)
plt.show()
