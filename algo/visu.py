import matplotlib.pyplot as plt
import sys

from pyrosm import OSM
from pyrosm import get_data

# Initialize the OSM parser object
osm = OSM(sys.argv[1])

# transit = osm.get_data_by_custom_criteria(
#     custom_filter={
#         'alt_name' : ["Canton de Vaud"]},
#     # Keep data matching the criteria above
#     filter_type="keep",
#     # Do not keep nodes (point data)    
#     keep_nodes=False, 
#     keep_ways=False, 
#     keep_relations=True)

#print (transit.geometry)
b = osm.get_buildings()
b.plot()

#drive_net = osm.get_network(network_type="driving")

#transit.plot()
#drive_net.plot()
plt.show()
