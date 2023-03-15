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

def displayClusteredNodes(graph, node_coords, clusters):
    '''Displays a clustered graph with one color per cluster'''
    colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    for n in range(len(clusters)):
        cluster = clusters[n]
        networkx.draw_networkx_nodes(graph, node_coords, cluster, node_size=20, node_color=colors[n%len(colors)])

def convertToDiGraph(osmGraph):
    '''converts a multipleDiGraph to a diGraph'''
    graph = networkx.DiGraph()
    for u,v,data in osmGraph.edges(data=True):
        w = data['length']
        if graph.has_edge(u,v):
            graph[u][v]['weight'] = min(w, graph[u][v]['weight'])
        else:
            graph.add_edge(u, v, weight=w)
    return graph


def IsNodeInternalToCluster(G: networkx.DiGraph, node, nodeToCluster):
    c = nodeToCluster[node]
    for p in graph[node]:
        if nodeToCluster[p] != c:
            return False
    return True    


def simplifyGraphWithPredicate(G: networkx.DiGraph, nodeToCluster):
    '''
    Loop over the graph until all nodes that match the supplied predicate 
    have been removed and their incident edges fused.
    '''
    g0 = G.copy()
    for node in G.nodes:
        if IsNodeInternalToCluster(G, node, nodeToCluster):
            in_edges_containing_node = list(g0.in_edges(node))
            out_edges_containing_node = list(g0.out_edges(node))
            for in_src, _ in in_edges_containing_node:
                for _, out_dst in out_edges_containing_node:
                    # g0.add_edge(in_src, out_dst)
                    dist = networkx.shortest_path_length(
                      g0, in_src, out_dst, weight='weight'
                    )
                    g0.add_edge(in_src, out_dst, weight=dist)
            g0.remove_node(node)
    return g0

# Get some multidigraph from openstreetmap and simplifies it
rawGraph = osmnx.graph_from_place("Chambery, France", network_type="drive")
projGraph = osmnx.project_graph(rawGraph)
osmGraph = osmnx.consolidate_intersections(projGraph, rebuild_graph=True, tolerance=30, dead_ends=True)
print(osmGraph)

# plot the street network with folium
m1 = osmnx.plot_graph_folium(osmGraph, popup_attribute="name", weight=2, color="#8b0000")
m1.save('osmGraph.html')

# convert it to digraph, keeping shortest route each time
graph = convertToDiGraph(osmGraph)
print(graph)

# extract node coordinates
node_coords = {}
for n in graph._node:
    node_coords[n] = (osmGraph._node[n]['x'], osmGraph._node[n]['y'])

# clusterize graph
clusters, nodeToCluster = clusterize(graph, node_coords, 3,3)
displayClusteredNodes(graph, node_coords, clusters)
plt.show()

# simplify graph
simpleGraph = simplifyGraphWithPredicate(graph, nodeToCluster)
print(simpleGraph)
simpleClusters = []
for c in clusters:
    simpleClusters.append([n for n in c if n in simpleGraph.nodes()])
displayClusteredNodes(simpleGraph, node_coords, simpleClusters)
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
                    if n2 in G[n1]:
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

def displayGraphWithRoute(G, clusters, node_coords, route):
    '''Displays a cluster graph with each cluster in a different color
       and traces the given route on top'''
    pairRoute = list(networkx.utils.pairwise(route))
    displayClusteredNodes(G, node_coords, clusters)
    networkx.draw_networkx_edges(H, node_coords, pairRoute, node_size=0, width=1)
    plt.show()

# create equivalent, non clusterd graph
H = clusteredToRegularGraph(simpleGraph, simpleClusters)

# compute best route in regular graph
HRoute = networkx.approximation.traveling_salesman_problem(H, cycle=False)

# display best route in regular graph
displayGraphWithRoute(simpleGraph, simpleClusters, node_coords, HRoute)

# get route in original clustered graph
GRoute = regularToClusterRoute(HRoute, nodeToCluster)

# display route
displayGraphWithRoute(simpleGraph, simpleClusters, node_coords, GRoute)
