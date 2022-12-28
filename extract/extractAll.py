import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import sys
import pickle

ox.config(log_console=True)

# returns the intersection of a set of ways and a given border (a polytgon)
# the returned result is a list of ids of the points at the end of way crossing
# the border, only the lowest id of the 2 is kept
def intersect(ways, border):
    res = []
    # for each way, id holds both ends of the way, while string is a linestring of the way
    for ids, string in ways.geometry.items():
        # intersect the line with the current border
        inter = border.geometry[0].intersection(string)
        # if string is inside the border, the intersection is the original line
        # otherwise, we cross the border
        if inter != string:
            a, b, c = ids
            res.append(min(a, b))
    return res

# Returns a list of places being entrance/exit point to the given place
def getExits(place, plot=False):
    border = ox.geocode_to_gdf(place)
    if plot:
        ax = border.plot()
        plt.show()
    streets_graph = ox.graph_from_place(place, network_type="bike", retain_all=True, truncate_by_edge=True)    
    streets_graph = ox.project_graph(streets_graph)
    streets = ox.utils_graph.graph_to_gdfs(streets_graph, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
    inter = intersect(streets, border)
    # caching output !
    fh = open(place+"-exits.pkl", 'wb')
    pickle.dump(inter, fh)

import threading

cantons = [
  #"Kanton Aargau",
  #"Kanton Appenzell Ausserrhoden",
  #"Kanton Appenzell Innerrhoden",
  #"Kanton Basel-Landschaft",
  #"Kanton Basel-Stadt",

  #  "Kanton Bern",

  "Canton de Fribourg",
  "Canton de Genève",
  "Kanton Glarus",
  "Kanton Graubünden",
  "Kanton Luzern",
  "Canton de Neuchâtel",
  "Kanton Nidwalden",
  "Kanton Obwalden",
  "Kanton Schaffhausen",
  "Kanton Schwyz",
  "Kanton Solothurn",
  "Kanton St. Gallen",
  "Kanton Thurgau",
  "Kanton Uri",
  "Canton de Vaud",
  "Kanton Zug",
  "Kanton Zürich",
  "Canton Ticino",
  "Canton du Jura",
  "Kanton Wallis",
]

#ts = []
for place in cantons:
  getExits(place, False)
  #t = threading.Thread(target=getExits, args=(place, False))
  #t.start()
  #ts.append(t)

#for t in ts:
#  t.join()

