import osmnx
import pickle
import sys, os
import networkx
import matplotlib.pyplot as plt

from RoadNetSimplifier import convertToDiGraph, simplifyGraphWithPredicate
from cluster import Cluster

basename = "Swiss" # Play
tol = ""
tolerance = 20000
subtolerance = 25
center = 46.3228088,6.2205695 # 47.3774417,8.5367355 - Zurich
graphName = "" #"Switzerland"

def getName(step, tol="20k"):
    return "%s%s%s.pkl" % (basename, step, tol)

def checkFile(name):
    return os.path.isfile(name)

def load(name):
    print ('Loading %s' % name)
    with open(name, 'rb') as file:
        return pickle.load(file)

def loadPolys():
    with open("CantonPolys.pkl", 'rb') as file:
        return pickle.load(file)

def get(tol):
    print ('Getting data')
    if graphName != '':
        rawGraph = osmnx.graph_from_place("Switzerland", network_type="bike")
    else:
        poly = osmnx.utils_geo.bbox_to_poly(*osmnx.utils_geo.bbox_from_point(center, tolerance))
        rawGraph = osmnx.graph.graph_from_polygon(poly, network_type="bike")
    with open(getName("Dump", tol), 'wb') as file:
        pickle.dump(rawGraph, file)
    return rawGraph

def project(rawGraph, tol):
    print ('Projecting')
    projGraph = osmnx.project_graph(rawGraph)
    with open(getName("Projected", tol), 'wb') as file:
        pickle.dump(projGraph, file)
    return projGraph

def consolidate(projGraph, tol):
    print ('Consolidating with 25m radius')
    osmGraph = osmnx.consolidate_intersections(projGraph, rebuild_graph=True, tolerance=subtolerance, dead_ends=False)
    print('Saving')
    with open(getName('Consolidated', tol), 'wb') as file:
        pickle.dump(osmGraph, file)
    return osmGraph

def getCluster(coords, hint, clusters):
    '''find the cluster for a given node, providing an hint
       which is a cluster most probably right, and thus to try first
       polys is the dictionnary of polygons defining clusters'''
    if hint:
        # try first our hint
        if hint.contains(coords):
            return hint
    for cluster in clusters:
        if cluster.contains(coords):
            return cluster
    return None

def convert(osmGraph, tol):
    clusterDefs = loadPolys().values()
    print ('Creating DiGraph')
    graph = convertToDiGraph(osmGraph)
    print(graph)
    print ('Extracting node coordinates')
    node_coords = {}
    clusters = [[] for n in range(len(clusterDefs))]
    nodeToCluster = {}
    curClus = None
    dropped = []
    for n in graph._node:
        coords = (osmGraph._node[n]['x'], osmGraph._node[n]['y'])
        c = getCluster(coords, curClus, clusterDefs)
        if c is None:
            dropped.append(n)
            continue # ignore that node, it's not inside the region of interest
        node_coords[n] = coords
        clusters[c.number].append(n)
        nodeToCluster[n] = c.number
        curClus = c
    # cleanup original graph
    for n in dropped:
        graph.remove_node(n)
    with open(getName('DiGraph', tol), 'wb') as file:
        pickle.dump((graph, node_coords, clusters, nodeToCluster), file)
    return graph, node_coords, clusters, nodeToCluster

def simplify(graph, node_coords, clusters, nodeToClusters, tol):
    print ('Simplifying graph')
    # implify step by step or the number of edges skyrockets and everything is slow
    sg = simplifyGraphWithPredicate(graph, nodeToClusters, 20)
    print(sg)
    sg = simplifyGraphWithPredicate(sg, nodeToClusters, 50)
    print(sg)
    sg = simplifyGraphWithPredicate(sg, nodeToClusters, 100)
    print(sg)
    sg = simplifyGraphWithPredicate(sg, nodeToClusters, 200)
    print(sg)
    sg = simplifyGraphWithPredicate(sg, nodeToClusters, None)
    print(sg)
    scoords = {n:c for n,c in node_coords.items() if n in sg}
    simpleClusters = []
    for c in clusters:
        simpleClusters.append([n for n in c if n in sg.nodes()])
    snodeToClusters = {n:c for n,c in nodeToClusters.items() if n in sg}
    with open(getName('SimpleGraph', tol), 'wb') as file:
        pickle.dump((sg, scoords, simpleClusters, snodeToClusters), file)
    return sg, scoords, simpleClusters, snodeToClusters

def computeDists(graph, tol):
    distances = dict(networkx.shortest_path_length(sg, weight='weight'))
    with open(getName('Distances', tol), 'wb') as file:
        pickle.dump(distances, file)
    return distances

def getRaw(tol):
    name = getName("Dump", tol)
    if checkFile(name):
        return load(name)
    else:
        return get(tol)

def getProjected(tol):
    name = getName("Projected", tol)
    if checkFile(name):
        return load(name)
    else:
        return project(getRaw(tol), tol)

def getConsolidated(tol):
    name = getName("Consolidated", tol)
    if checkFile(name):
        return load(name)
    else:
        return consolidate(getProjected(tol), tol)

def getDiGraph(tol):
    name = getName('DiGraph', tol)
    if checkFile(name):
        return load(name)
    else:
        return convert(getConsolidated(tol), tol)

def getSimpleGraph(tol):
    name = getName('SimpleGraph', tol)
    if checkFile(name):
        return load(name)
    else:
        return simplify(*getDiGraph(tol), tol)

def getDistances(tol):
    name = getName('Distances', tol)
    if checkFile(name):
        return load(name)
    else:
        sg, snode_coords, simpleClusters, snodeToClusters = getSimpleGraph(tol)
        return computeDists(sg, tol)
    
    
colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# graph, node_coords, clusters, nodeToClusters = getDiGraph(tol)
# print (graph)
# plt.figure(1)
# for n in range(len(clusters)):
#     networkx.draw_networkx_nodes(graph, node_coords, clusters[n], node_size=20, node_color=colors[n%len(colors)])

sg, snode_coords, simpleClusters, snodeToClusters = getSimpleGraph(tol)
print(sg)
plt.figure(2)
for n in range(len(simpleClusters)):
    networkx.draw_networkx_nodes(sg, snode_coords, simpleClusters[n], node_size=20, node_color=colors[n%len(colors)])
#networkx.draw_networkx_edges(sg, snode_coords, node_size=0, width=1)

# build full table of weights
distances = getDistances(tol)

plt.show()

