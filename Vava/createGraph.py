import osmnx
import pickle
import sys, os
import networkx
import matplotlib.pyplot as plt

from cluster import Cluster

basename = "Swiss"
tol = ""
tolerance = 20000
subtolerance = 25

useful_tags_path = ['highway', 'surface']
osmnx.settings.useful_tags_way=useful_tags_path

def badSurface(s):
    if isinstance(s, list):
        for t in s:
            if badSurface(t): return True
        return False
    if ':' in s : s = s[:s.find(':')]
    if s in ['paved', 'asphalt', 'chipseal', 'concrete', 'paving_stones', 'sett', 'brick', 'metal', 'wood', 'compacted']:
        return False
    return True

slowness = {
    'paved' : 1,
    'asphalt' : 1,
    'chipseal' : 1.1,
    'concrete' : 1.1,
    'paving_stones': 1.5,
    'sett' : 1.3,
    'brick' : 1.2,
    'metal': 1.2,
    'wood' : 1.2,
    'compacted' : 2,
}

def surfaceSlowness(s):
    if isinstance(s, list):
        r = 1
        for t in s:
            r = min(r, surfaceSlowness(t))
        return r
    if ':' in s : s = s[:s.find(':')]
    return slowness[s]

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
    # buffer_dist is there to cover inclusions of Germany in switzerland...
    rawGraph = osmnx.graph_from_place("Switzerland", simplify=True, network_type="bike", buffer_dist=2000)
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

clusterDefs = loadPolys().values()

protectedPlaces = {'Campione d\'Italia': (9008012407, 'Canton Ticino'), 'Busingen': (390407244, 'Schaffouse or Turgovie'), 'alte Rheinbrücke': (1378764555, 'Kanton St. Gallen'), 'Pont de Grilly': (1186596358, 'Canton de Geneve'), 'Rheinbrücke': (176724546, 'Kanton St. Gallen'), 'BERN': (33202504, 'Kanton Bern')}
protectedNodes = [a for a,b in protectedPlaces.values()]

def convertToDiGraph(osmGraph):
    '''converts a multipleDiGraph to a diGraph
       and drops edges with identical src and dst'''
    graph = networkx.DiGraph()
    osmidToNode = {}
    for u,v,data in osmGraph.edges(data=True):
        if u == v: continue
        slowFactor = 1
        highway = data['highway']
        if highway in ('path', 'track') or 'path' in highway or 'track' in highway:
            if 'surface' in data:
                s = data['surface']
                if badSurface(s): continue
                slowFactor = surfaceSlowness(s)
            else:
                slowFactor = 2
        if highway == 'service' or 'service' in highway:
            slowfactor = 1.5
        w = data['duration']
        if graph.has_edge(u,v):
            if w < graph[u][v]['weight']:
                graph[u][v]['weight'] = w
                graph[u][v]['slowFactor'] = slowFactor
        else:
            graph.add_edge(u, v, weight=w, slowFactor=slowFactor)
    for n in osmGraph._node:
        l = osmGraph._node[n]['osmid_original']
        if isinstance(l, str):
            for ll in [int(c) for c in l[1:-1].split(',')]:
                for p in protectedNodes:
                    if p == ll:
                        osmidToNode[p] = n
        else:
            for p in protectedNodes:
                if p == l:
                    osmidToNode[p] = n
    return graph, osmidToNode

def convert(osmGraph, tol):
    print ('Creating DiGraph')
    graph, osmidToNode = convertToDiGraph(osmGraph)
    print(graph)
    print ('Extracting node coordinates')
    node_coords = {}
    clusters = [[] for n in range(len(clusterDefs))]
    nodeToCluster = {}
    curClus = None
    #dropped = []
    for n in graph._node:
        coords = (osmGraph._node[n]['x'], osmGraph._node[n]['y'])
        c = getCluster(coords, curClus, clusterDefs)
        #if c is None and n not in osmidToNode.values():
        #    dropped.append(n)
        #    continue # ignore that node, it's not inside the region of interest
        node_coords[n] = coords
        if c :
            clusters[c.number].append(n)
        nodeToCluster[n] = c.number if c else -1
        if c:
            curClus = c
    # cleanup original graph
    #for n in dropped:
    #    graph.remove_node(n)
    with open(getName('DiGraph', tol), 'wb') as file:
        pickle.dump((graph, node_coords, clusters, nodeToCluster, osmidToNode), file)
    return graph, node_coords, clusters, nodeToCluster, osmidToNode

def IsNodeInternalToCluster(G: networkx.DiGraph, node, nodeToCluster):
    c = nodeToCluster[node]
    for p, _ in G.in_edges(node):
        if nodeToCluster[p] != c:
            return False
    for _, p in G.out_edges(node):
        if nodeToCluster[p] != c:
            return False
    return True

def simplifyGraph(G: networkx.DiGraph, nodeToCluster, droppedClusters, protectedOsmId, maxCon=None):
    '''
    Remove internal nodes of each cluster, keeping the connectivity and
    computing the new weight as the lowest weight of all connections
    '''
    g0 = G.copy()
    for node in G.nodes:
        if node in protectedOsmId: continue
        if nodeToCluster[node] in droppedClusters or IsNodeInternalToCluster(g0, node, nodeToCluster):
            in_edges_containing_node = list(g0.in_edges(node))
            out_edges_containing_node = list(g0.out_edges(node))
            if maxCon and (len(set(in_edges_containing_node + out_edges_containing_node)) > maxCon): continue
            for in_src, _ in in_edges_containing_node:
                for _, out_dst in out_edges_containing_node:
                    if in_src == out_dst: continue
                    dist = g0[in_src][node]['weight'] + g0[node][out_dst]['weight']
                    if out_dst in g0[in_src]:
                        # if already connected, keep a single connection
                        g0[in_src][out_dst]['weight'] = min(dist, g0[in_src][out_dst]['weight'])
                    else:
                        g0.add_edge(in_src, out_dst, weight=dist)
                        #if nodeToCluster[in_src] != nodeToCluster[out_dst]:
                        #    print('AIE', in_src, out_dst, nodeToCluster[in_src], nodeToCluster[out_dst])
            g0.remove_node(node)
    return g0

def simplify(graph, node_coords, clusters, nodeToClusters, osmidToNode, tol):
    print(osmidToNode)
    print ('Simplifying graph')
    protectedOsmId = [osmidToNode[id] for id in protectedNodes]
    droppedClusters = [nodeToClusters[osmidToNode[a]] for a in protectedNodes]
    # implify step by step or the number of edges skyrockets and everything is slow
    sg = simplifyGraph(graph, nodeToClusters, droppedClusters, protectedOsmId, 20)
    print(sg)
    sg = simplifyGraph(sg, nodeToClusters, droppedClusters, protectedOsmId, 50)
    print(sg)
    sg = simplifyGraph(sg, nodeToClusters, droppedClusters, protectedOsmId, 100)
    print(sg)
    sg = simplifyGraph(sg, nodeToClusters, droppedClusters, protectedOsmId, 200)
    print(sg)
    sg = simplifyGraph(sg, nodeToClusters, droppedClusters, protectedOsmId, 400)
    print(sg)
    sg = simplifyGraph(sg, nodeToClusters, droppedClusters, protectedOsmId, 600)
    print(sg)
    sg = simplifyGraph(sg, nodeToClusters, droppedClusters, protectedOsmId, 800)
    print(sg)
    sg = simplifyGraph(sg, nodeToClusters, droppedClusters, protectedOsmId, None)
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

