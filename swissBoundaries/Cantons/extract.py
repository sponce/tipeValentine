import json

# First create one geojson file per connex component
data = json.loads(open('swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.geojson', 'rb').read())

cantons_nb = {}

for feat in data['features']:
    props = feat["properties"]
    num = int(props["KANTONSNUM"])
    subnum = 0
    if num in cantons_nb:
        subnum = cantons_nb[num] + 1
    cantons_nb[num] = subnum
    cantonName = props["NAME"]
    name = "Canton-%s-%d" % (cantonName, subnum)
    # drop 3rd coordinate in geometry
    coords = feat["geometry"]["coordinates"]
    newCoords = []
    for string in coords:
        newCoords.append([ [lat,lon] for lat,lon,alt in string])
    feat["geometry"] = { "type" : "Polygon",
                         "coordinates" : newCoords }
    subdata = json.dumps({ "type" : "FeatureCollection",
                           "name" : name,
                           "features" : [ feat ] })
    open('%s.geojson' % name, 'wb').write(subdata)
    
