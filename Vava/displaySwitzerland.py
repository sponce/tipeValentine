import osmnx
import pickle
import networkx
import matplotlib.pyplot as plt

print ('Loading')
with open('SwissConsolidated500.pkl', 'rb') as file:
    osmGraph = pickle.load(file)

print (osmGraph)
m1 = osmnx.plot_graph_folium(osmGraph, popup_attribute="name", weight=2, color="#8b0000")
m1.save('osmGraph.html')

print ('Loading')
with open('SwissDiGraph.pkl', 'rb') as file:
    graph, node_coords = pickle.load(file)

print (graph)

#networkx.draw_networkx_nodes(graph, node_coords, node_size=20)
#networkx.draw_networkx_edges(graph, node_coords, node_size=0, width=1)
#plt.show()
