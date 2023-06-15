import json
import pickle

from cluster import Cluster

# First create one geojson file per connex component
data = json.loads(open('../swissBoundaries/Cantons/swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.geojson', 'rb').read())

nameToCanton = {}

n = 0
for feat in data['features']:
    props = feat["properties"]
    cantonName = props["NAME"]
    if cantonName not in nameToCanton:
        canton = Cluster(cantonName, n)
        nameToCanton[cantonName] = canton
        n += 1
    canton = nameToCanton[cantonName]
    # drop 3rd coordinate in geometry
    coords = feat["geometry"]["coordinates"]
    newCoords = []
    for string in coords:
        canton.addPoly([ (lat,lon) for lat,lon,alt in string])
    
with open("CantonPolys", 'wb') as file:
    pickle.dump(nameToCanton, file)
