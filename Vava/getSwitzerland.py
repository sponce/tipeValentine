import osmnx
import pickle

# Get some multidigraph from openstreetmap and simplifies it
rawGraph = osmnx.graph_from_place("Switzerland", network_type="bike")
with open('SwissDump', 'wb') as file:
    pickle.dump(rawGraph, file)
