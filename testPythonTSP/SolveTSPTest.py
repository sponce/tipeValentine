from SolveTSP import completeGraph, solveGreedyWithClusters
import pickle
import matplotlib.pyplot as plt
from Utils import displayGraphWithRoute, displayClusteredNodes, displayGraphWithEdges
        
with open('SimpleGraph.dump', 'rb') as file:
    G, clusters, node_coords, route = pickle.load(file)

print(G)
H = completeGraph(G)
#print(clusters)
#displayGraphWithRoute(H, clusters, node_coords, route)
#displayGraphWithEdges(G, clusters, node_coords)
#plt.show()

n = clusters[0][0]
print(clusters[0])
print(clusters[1])
print(n, node_coords[n])
route = solveGreedyWithClusters(H, clusters[:2], n, 0)
print(route)
plt.figure(0)
displayGraphWithEdges(H, clusters, node_coords)
plt.figure(1)
displayGraphWithRoute(H, clusters, node_coords, route)
plt.show()
