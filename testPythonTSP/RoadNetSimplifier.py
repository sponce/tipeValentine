'''
In a realistic sluctered route graph, one can simplify the problem
of finding the shortest route going through all clusters by dropping
all nodes and routes internal to each cluster.
Alternatively, if a list of mandatory nodes is given, one can drop
all other nodes of the clusters in which they are
'''
import osmnx
import networkx
import math
import matplotlib.pyplot as plt
from Utils import displayClusteredNodes, displayGraphWithRoute, displayGraphWithEdges

def clusterize(G, nodes, NX, NY):
    '''Create artificially rectangle clusters in a non clustered problem
    Nodes are clusted on a grix NX x NY
    G is the graph to cluster, node_coords the definition of each node of G
    and Nx, NY the number of clusters in each direction
    '''
    minX = min([nodes[n][0] for n in G._node])-0.001
    maxX = max([nodes[n][0] for n in G._node])+0.001
    minY = min([nodes[n][1] for n in G._node])-0.001
    maxY = max([nodes[n][1] for n in G._node])+0.001
    clusters = [[] for n in range(NX*NY)]
    nodeToCluster = {}
    for n in G._node:
        x = nodes[n][0]
        y = nodes[n][1]
        nx = math.trunc(NX*(x-minX)/(maxX-minX))
        ny = math.trunc(NY*(y-minY)/(maxY-minY))
        cluster = ny*NX+nx
        clusters[cluster].append(n)
        nodeToCluster[n] = cluster
    return clusters, nodeToCluster

def convertToDiGraph(osmGraph):
    '''converts a multipleDiGraph to a diGraph
       and drops edges with identical src and dst'''
    graph = networkx.DiGraph()
    for u,v,data in osmGraph.edges(data=True):
        if u == v: continue
        w = data['length']
        if graph.has_edge(u,v):
            graph[u][v]['weight'] = min(w, graph[u][v]['weight'])
        else:
            graph.add_edge(u, v, weight=w)
    return graph

def IsNodeInternalToCluster(G: networkx.DiGraph, node, nodeToCluster):
    c = nodeToCluster[node]
    for p, _ in G.in_edges(node):
        if nodeToCluster[p] != c:
            return False
    for _, p in G.out_edges(node):
        if nodeToCluster[p] != c:
            return False
    return True    

def simplifyGraphWithPredicate(G: networkx.DiGraph, nodeToCluster):
    '''
    Remove internal nodes of each cluster, keeping the connectivity and
    computing the new weight as the lowest weight of all connections
    '''
    g0 = G.copy()
    for node in G.nodes:
        if IsNodeInternalToCluster(g0, node, nodeToCluster):
            in_edges_containing_node = list(g0.in_edges(node))
            out_edges_containing_node = list(g0.out_edges(node))
            for in_src, _ in in_edges_containing_node:
                for _, out_dst in out_edges_containing_node:
                    if in_src == out_dst: continue
                    dist = g0[in_src][node]['weight'] + g0[node][out_dst]['weight']
                    if out_dst in g0[in_src]:
                        # if already connected, keep a single connection
                        g0[in_src][out_dst]['weight'] = min(dist, g0[in_src][out_dst]['weight'])
                    else:
                        g0.add_edge(in_src, out_dst, weight=dist)
                        if nodeToCluster[in_src] != nodeToCluster[out_dst]:
                            print('AIE', in_src, out_dst, nodeToCluster[in_src], nodeToCluster[out_dst])
            g0.remove_node(node)
    return g0

def clusteredToRegularGraph(G, completeG, clusters):
    '''create a regular graph from a clustered graph 5.2.2 of the thesis'''
    H = networkx.Graph()
    # same nodes
    for node in G.nodes(): H.add_node(node)
    # 0 weight in each subcluster cycle
    for cluster in clusters:
        for i in range(1, len(cluster)):
            H.add_edge(cluster[i-1], cluster[i], weight=0)
        if len(cluster) > 1:
            H.add_edge(cluster[-1], cluster[0], weight=0)
    # edges from subcluster to other subclusters
    for a in range(len(clusters)):
        for b in range(len(clusters)):
            if a == b: break
            for i1 in range(len(clusters[a])):
                n1 = clusters[a][i1]
                np1 = clusters[a][i1-1] if i1 > 0 else clusters[a][-1]
                for n2 in clusters[b]:
                    if n2 in G[np1]:
                        path = osmnx.distance.shortest_path(completeG, n1, n2)
                        if path:
                            H.add_edge(np1, n2, weight=sum([completeG[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)]))
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
