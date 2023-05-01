import osmnx
import networkx
import pickle
import matplotlib.pyplot as plt
from Utils import displayGraphWithRoute, displayClusteredNodes, displayGraphWithEdges
from RoadNetSimplifier import clusterize, convertToDiGraph, IsNodeInternalToCluster, simplifyGraphWithPredicate, clusteredToRegularGraph, regularToClusterRoute
from SolveTSP import completeGraph, solveGreedyWithClusters

simpleGraph = networkx.Graph()
simpleGraph.add_edge(1, 2, weight=1)
simpleGraph.add_edge(1, 3, weight=1)
simpleGraph.add_edge(2, 4, weight=1)
simpleGraph.add_edge(3, 4, weight=1)
simpleGraph.add_edge(11, 12, weight=1)
simpleGraph.add_edge(11, 13, weight=1)
simpleGraph.add_edge(12, 14, weight=1)
simpleGraph.add_edge(13, 14, weight=1)
simpleGraph.add_edge(11, 2, weight=2)
simpleGraph.add_edge(2, 11, weight=2)
simpleGraph.add_edge(4, 13, weight=3)
simpleGraph.add_edge(21, 22, weight=1)
simpleGraph.add_edge(21, 23, weight=1)
simpleGraph.add_edge(22, 24, weight=1)
simpleGraph.add_edge(23, 24, weight=1)
simpleGraph.add_edge(12, 21, weight=2)
simpleGraph.add_edge(14, 23, weight=3)
simpleGraph.add_edge(4, 24, weight=1)
simpleClusters=[[1,2,3,4],[11,12,13,14], [21,22,23,24]]
node_coords={1:(0,.2),
             2:(1,0.3),
             3:(0,1.2),
             4:(1,1.3),
             11:(3,0),
             12:(4,0.2),
             13:(3,1),
             14:(4,1.2),
             21:(6,0.3),
             22:(7,0.5),
             23:(6,1.3),
             24:(7,1.5)}
nodeToCluster={}
for i in range(len(simpleClusters)):
    for n in simpleClusters[i]:
        nodeToCluster[n] = i

plt.figure(1)
displayGraphWithEdges(simpleGraph, simpleClusters, node_coords, drawLabels=True)
plt.draw()
plt.figure(2)
# create equivalent, non clusterd graph
S = completeGraph(simpleGraph)
GR = clusteredToRegularGraph(simpleGraph, S, simpleClusters)
displayGraphWithEdges(GR, simpleClusters, node_coords, drawLabels=True)

print(GR)
H = completeGraph(GR)
plt.figure(3)
displayGraphWithEdges(H, simpleClusters, node_coords, drawLabels=True)

n = simpleClusters[0][0]
print(simpleClusters[0])
print(simpleClusters[1])
print(n, node_coords[n])
route = solveGreedyWithClusters(H, simpleClusters, n, 0)
print(route)
displayGraphWithEdges(H, simpleClusters, node_coords)
plt.figure(4)
displayGraphWithRoute(H, simpleClusters, node_coords, route)
plt.figure(5)
GRoute = regularToClusterRoute(route, nodeToCluster)
displayGraphWithRoute(H, simpleClusters, node_coords, GRoute)
plt.show()
