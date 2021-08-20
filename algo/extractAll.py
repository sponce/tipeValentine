import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import sys
import pickle

ox.config(log_console=True)

#G = ox.graph_from_place("Canton de Genève", network_type="bike", retain_all=True, truncate_by_edge=True)
#G = ox.graph_from_place("Versoix", network_type="bike", retain_all=True, truncate_by_edge=True)
#ox.osm_xml.save_graph_xml(G, filepath='versoix.osm')
#print (G.nodes)
#print (g[774807223])
#G = ox.graph_from_xml(sys.argv[1])
#fig, ax = ox.plot_graph(G)

# Versoix boundary (from https://www.openstreetmap.org/relation/1685541)


# returns the intersection of a set of ways and a given border (a polytgon)
# the returned result is a list of tuples (coordinate, way)
# with the exact intersection point and the way concerned
def intersect(ways, border):
    res = []
    for id, string in ways.geometry.items():
        inter = border.geometry[0].intersection(string)
        if inter != string:
            try:
                rem = list((set(inter.coords)-set(string.coords)))
                if len(rem) > 0:
                    res.append((id, rem[0]))
            except(Exception):
                # we can safely ignore lines
                pass
    return res

# Returns a list of places being entrance/exit point to the given place
def getExits(place, plot=False):
    border = ox.geocode_to_gdf(place)
    border = border.to_crs("CRS")
    if plot:
        ax = border.plot()
    streets_graph = ox.graph_from_place(place, network_type="bike", retain_all=True, truncate_by_edge=True)
    streets_graph = ox.project_graph(streets_graph)
    streets = ox.utils_graph.graph_to_gdfs(streets_graph, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
    streets = streets.to_crs("CRS")
    if plot:
        streets.plot(ax = ax, color='black')
    inter = intersect(streets, border)
    if plot:
        target_streets = streets.loc[[id for id,coords in inter]]
        for id, coords in inter:
            ax.plot(*coords, 'gx')   
        target_streets.plot(ax=ax, color='red')
        plt.show()
    output = [c for c,w in inter]
    # caching output !
    fh = open(place+"-exits.pkl", 'wb')
    pickle.dump(output, fh)
    return output

import threading

cantons = [
  "Kanton Aargau",
  "Kanton Appenzell Ausserrhoden",
  "Kanton Appenzell Innerrhoden",
  "Kanton Basel-Landschaft",
  "Kanton Basel-Stadt",
  "Kanton Bern",
  "Canton de Fribourg",
#  "Canton de Genève",
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
#  "Canton de Vaud",
  "Kanton Zug",
  "Kanton Zürich",
  "Canton Ticino",
  "Canton du Jura",
  "Kanton Wallis",
]

ts = []
for place in cantons:
  t = threading.Thread(target=getExits, args=(place, False))
  t.start()
  ts.append(t)

for t in ts:
  t.join()

