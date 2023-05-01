import osmnx
import networkx
import pickle
import matplotlib.pyplot as plt
from Utils import displayGraphWithRoute, displayClusteredNodes, displayGraphWithEdges

def completeGraph(G):
    H = G.copy()
    for n in G.nodes:
        for p in G.nodes:
            if p == n: continue
            if not G.has_edge(n,p):
                path = osmnx.distance.shortest_path(G, n, p)
                if path:
                    H.add_edge(n, p, weight=sum([G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)]))
                else:
                    print ("No path from", n, "to", p)
    return H

def findClosestNode(G, n, nodes):
    '''
    find closest node to n in the given set
    '''
    minDist = 99999999999999
    bestNode = -1
    for p in nodes:
        if G.has_edge(n,p):
            dist = G[n][p]['weight']
            if dist < minDist:
                minDist = dist
                bestNode = p
    return p

def findClosestNodeInClusters(G, n, clusters, clustersLeft):
    '''
    find closest node to n in the given set
    '''
    minDist = 99999999999999
    bestNode = -1
    bestClus = -1
    for i in range(len(clusters)):
        if i in clustersLeft:
            for p in clusters[i]:
                if n == p: continue
                if G.has_edge(n,p):
                    dist = G[n][p]['weight']
                    if dist < minDist:
                        print(n, p, i, dist, minDist)
                        minDist = dist
                        bestNode = p
                        bestClus = i
    return bestNode, bestClus

def solveGreedyWithClusters(G, clusters, start, curClusterN):
    '''
    Solves TSP with Greedy algorithms, respecting clusters,
    that is taking a single node of each cluster
    '''
    path = [start]
    clustersLeft = list(range(len(clusters)))
    clustersLeft.remove(curClusterN)
    while len(clustersLeft) > 0:
        p, curClusterN = findClosestNodeInClusters(G, path[-1], clusters, clustersLeft)
        print (p, curClusterN, path)
        path.append(p)
        clustersLeft.remove(curClusterN)
    return path
