import osmnx
import pickle

print ('Loading')
with open('SwissDump.pkl', 'rb') as file:
    rawGraph = pickle.load(file)
print ('Projecting')
projGraph = osmnx.project_graph(rawGraph)
with open('SwissProjected.pkl', 'wb') as file:
    pickle.dump(projGraph, file)
print ('Consolidating with 500m radius')
osmGraph = osmnx.consolidate_intersections(projGraph, rebuild_graph=True, tolerance=500, dead_ends=False)
print('Saving')
with open('SwissConsolidated.pkl', 'wb') as file:
    pickle.dump(osmGraph, file)

