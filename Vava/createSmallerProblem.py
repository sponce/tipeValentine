import pickle
import networkx
import matplotlib.pyplot as plt

from RoadNetSimplifier import IsNodeInternalToCluster

# This starts from the full swiss problem and keeps only 5 cantons, namely
keptNames = ['Bern', 'Valais', 'Vaud', 'Fribourg', 'Genève']

with open("CantonPolys.pkl", 'rb') as file:
    cantons = pickle.load(file)

keptNumbers = []
for name in cantons:
    if name in keptNames:
        keptNumbers.append(cantons[name].number)        
print (keptNumbers)

# load big problem
name = "SwissSimpleGraph.pkl"
print ('Loading %s' % name)
with open(name, 'rb') as file:
    g, node_coords, clusters, nodeToClusters = pickle.load(file)

# simplify the graph
ng = g.copy()
for n in g:
    if nodeToClusters[n] not in keptNumbers:
        ng.remove_node(n)
print (ng)

# simplify clusters and coordinates
ncoords = {n:c for n,c in node_coords.items() if n in ng}
nclusters = []
for n in range(len(clusters)):
    nclusters.append([p for p in clusters[n] if p in ng] if n in keptNumbers else [])
nn2c = {n:c for n,c in nodeToClusters.items() if n in ng}

colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
plt.figure(1)
print ([len (c) for c in nclusters])
for n in keptNumbers:
    networkx.draw_networkx_nodes(ng, ncoords, nclusters[n], node_size=20, node_color=colors[n%len(colors)])

# simplify further by dropping nodes not having anymore connections outside their cluster
g = ng
ng = g.copy()
for node in g.nodes:
    if IsNodeInternalToCluster(ng, node, nn2c):
        ng.remove_node(node)
print (ng)

# rename clusters
cRename = {}
i = 0
for n in keptNumbers:
    cRename[n] = i
    i += 1

# recompute clusters and coordinates
ncoords = {n:c for n,c in node_coords.items() if n in ng}
nclusters = [[] for n in range(len(cRename.keys()))]
for n in range(len(clusters)):
    if n in keptNumbers:
        nclusters[cRename[n]] = [p for p in clusters[n] if p in ng]
nn2c = {n:cRename[c] for n,c in nodeToClusters.items() if n in ng}

plt.figure(2)
print ([len (c) for c in nclusters])
for n in range(len(nclusters)):
    networkx.draw_networkx_nodes(ng, ncoords, nclusters[n], node_size=20, node_color=colors[n%len(colors)])

plt.show()

with open("SmallPbSimpleGraph.pkl", 'wb') as file:
    pickle.dump((ng, ncoords, nclusters, nn2c), file)

# load distances
name = 'SwissDistances.pkl'
print ('Loading %s' % name)
with open(name, 'rb') as file:
    distances = pickle.load(file)

nd = {n:{p:dd for p,dd in d.items() if p in ng} for n,d in distances.items() if n in ng}
with open("SmallPbDistances.pkl", 'wb') as file:
    pickle.dump(nd, file)
print ("Done")
