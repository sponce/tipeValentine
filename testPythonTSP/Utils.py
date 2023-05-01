import networkx
import matplotlib.pyplot as plt

def displayClusteredNodes(graph, node_coords, clusters, drawLabels=False):
    '''Displays a clustered graph with one color per cluster'''
    colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    for n in range(len(clusters)):
        cluster = clusters[n]
        networkx.draw_networkx_nodes(graph, node_coords, cluster, node_size=20, node_color=colors[n%len(colors)])
    if drawLabels:
        networkx.draw_networkx_labels(graph, node_coords)

def displayGraphWithRoute(G, clusters, node_coords, route):
    '''Displays a cluster graph with each cluster in a different color
       and traces the given route on top'''
    pairRoute = list(networkx.utils.pairwise(route))
    displayClusteredNodes(G, node_coords, clusters)
    networkx.draw_networkx_edges(G, node_coords, pairRoute, node_size=0, width=1)
    plt.draw()

def displayGraphWithEdges(G, clusters, node_coords, drawLabels=False, drawLabels2=False):
    '''Displays a cluster graph with each cluster in a different color
       and traces the given route on top'''
    displayClusteredNodes(G, node_coords, clusters, drawLabels)
    networkx.draw_networkx_edges(G, node_coords, node_size=0, width=1)
    if drawLabels:
        labels = networkx.get_edge_attributes(G,'weight')
        networkx.draw_networkx_edge_labels(G,node_coords,edge_labels=labels)
    if drawLabels2:
        networkx.draw_networkx_labels(G, node_coords, verticalalignment="top")
    plt.draw()
