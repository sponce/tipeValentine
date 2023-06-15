import osmnx
import pickle

from RoadNetSimplifier import convertToDiGraph

print ('Loading')
with open('SwissConsolidated500.pkl', 'rb') as file:
    osmGraph = pickle.load(file)
print ('Creating DiGraph')
graph = convertToDiGraph(osmGraph)
print ('Extracting node coordinates')
node_coords = {}
for n in graph._node:
    node_coords[n] = (osmGraph._node[n]['x'], osmGraph._node[n]['y'])
with open('SwissDiGraph.pkl', 'wb') as file:
    pickle.dump((graph, node_coords), file)
