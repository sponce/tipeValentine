import geojson
import pickle

from cluster import Cluster

# First create one geojson file per connex component
data = geojson.loads(open('../swissBoundaries/Cantons/swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.geojson', 'rb').read())

nameToCanton = {}

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from shapely.geometry import shape

# Plots a Polygon to pyplot `ax`
# def plot_polygon(ax, poly, **kwargs):
#     path = Path.make_compound_path(
#         Path(np.asarray(poly.exterior.coords)[:, :2]),
#         *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

#     patch = PathPatch(path, **kwargs)
#     collection = PatchCollection([patch], **kwargs)
    
#     ax.add_collection(collection, autolim=True)
#     ax.autoscale_view()
#     return collection

# print(data.keys())

n = 0
for feat in data['features']:
    props = feat["properties"]
    cantonName = props["NAME"]
    main = False
    print (cantonName)
    if cantonName not in nameToCanton:
        canton = Cluster(cantonName, n)
        nameToCanton[cantonName] = canton
        n += 1
        main = True
    canton = nameToCanton[cantonName]
    # drop 3rd coordinate in geometry
    coords = feat["geometry"]["coordinates"]
    newCoords = []
    for string in coords:
        canton.addPoly(shape(feat['geometry']))
    
with open("CantonPolys.pkl", 'wb') as file:
    pickle.dump(nameToCanton, file)
