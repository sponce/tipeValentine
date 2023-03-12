import math
import tsplib95
import networkx
import numpy as np
import matplotlib.pyplot as plt

def displayClusteredNodes(graph, clusters):
    '''Displays a clustered graph with one color per cluster'''
    colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    for n in range(len(clusters)):
        cluster = clusters[n]
        networkx.draw_networkx_nodes(graph, problem.node_coords, cluster, node_size=20, node_color=colors[n%len(colors)]);

def displayGraphWithRoute(G, clusters, route):
    '''Displays a cluster graph with each cluster in a different color
       and traces the given route on top'''
    pairRoute = list(networkx.utils.pairwise(route))
    displayClusteredNodes(G, clusters)
    networkx.draw_networkx_edges(H, problem.node_coords, pairRoute, node_size=0, width=1)
    plt.show()

def clusteredToRegularGraph(G, clusters):
    '''create a regular graph from a clusterd graph 5.2.2 of the thesis'''
    P2 = 8000*len(clusters) # sth > min Tour len * nb subclusters
    H = networkx.Graph()
    # same nodes
    for node in G.nodes(): H.add_node(node)
    # 0 weight in each subcluster cycle
    for cluster in clusters:
        for i in range(1, len(cluster)):
            H.add_edge(cluster[i-1], cluster[i], weight=0)
        H.add_edge(cluster[-1], cluster[0], weight=0)
    # edges from subcluster to other subclusters
    for a in range(len(clusters)):
        for b in range(len(clusters)):
            if a == b: break
            for i1 in range(len(clusters[a])):
                n1 = clusters[a][i1]
                np1 = clusters[a][i1-1] if i1 > 0 else clusters[a][-1]
                for n2 in clusters[b]:
                    H.add_edge(n1, n2, weight=G[n1][n2]['weight'])
    return H

def regularToClusterRoute(HRoute, nodeToCluster):
    '''converts route in regular graph issued from a clustered one
       to the route in the original graph'''
    firstNode = HRoute[0]
    GRoute = [firstNode,]
    lastclus = nodeToCluster[firstNode]
    for v in HRoute[1:]:
        clus = nodeToCluster[v]
        if lastclus != clus:
            GRoute.append(v)
            lastclus = clus
    return GRoute

def clusterize(problem, NX, NY):
    '''Create artificially clusters in a non clustered problem
    Nodes are clusted on a grix NX x NY'''
    maxX = max([pos[0] for name, pos in problem.node_coords.items()])+1
    maxY = max([pos[1] for name, pos in problem.node_coords.items()])+1
    clusters = [[] for n in range(NX*NY)]
    nodeToCluster = {}
    for n in problem.get_nodes():
        x,y = problem.node_coords[n]
        nx = math.trunc(NX*x/maxX)
        ny = math.trunc(NY*y/maxY)
        cluster = ny*NX+nx
        clusters[cluster].append(n)
        nodeToCluster[n] = cluster
    return clusters, nodeToCluster

# extract problem with tsplib
problem = tsplib95.load('ch130.tsp')
G = problem.get_graph()

# clusterize problem
clusters, nodeToCluster = clusterize(problem, 2, 3)

# create equivalent, non clusterd graph
H = clusteredToRegularGraph(G, clusters)

# compute best route in regular graph
HRoute = networkx.approximation.traveling_salesman_problem(H, cycle=False)

# display best route in regular graph
displayGraphWithRoute(G, clusters, HRoute)

# get route in original clustered graph
GRoute = regularToClusterRoute(HRoute, nodeToCluster)

# display route
displayGraphWithRoute(G, clusters, GRoute)
