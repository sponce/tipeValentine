import pickle
import requests
import json
import subprocess
import time

fh = open("InputNodes.pkl", 'rb')
points, additions, allNodes = pickle.load(fh)

def close(ca, cb):
    dx = ca[0] - cb[0]
    dy = ca[1] - cb[1]
    return dx*dx+dy*dy < 0.01

def cleanup(name, ids, coords):
    nborig = len(ids)
    nids = []
    ncoords = []
    for n in range(len(ids)):
        ca = coords[n]
        hit = None
        for cb in ncoords:
            if close(ca, cb):
                hit = cb
                break
        if not hit:
            nids.append(ids[n])
            ncoords.append(coords[n])
    print ("%s : went from %d to %d nodes" % (name, nborig, len(nids)))
    return nids, ncoords

def getWeight(ca, cb):
    params = { "point": [ "%s,%s" % ca, "%s,%s" % cb ],
               "vehicle": "car",
               "instructions" : "false",
               "calc_points": "false",
               "out_arrays": [ "weights"],
              }
    resp = requests.get('http://localhost:8989/route', params=params)
    r = json.loads(resp.text)
    if 'paths' in r:
        return (r['paths'][0]['time'])
    return None

additions = { "Canton de Genève" : [(871856370, (46.24251457663374,6.141149673014845))],
              "Kanton St. Gallen" : [(4466095934, (47.41304052848629,9.165194684131343)), (1286482374,(47.00377668473661,9.500952243128225))],
              "Canton de Fribourg" : [(320349073, (46.61021834939049,7.288543268752914))],
              "Kanton Wallis" : [(3041241876,(46.48608697912633,8.262544643612959))],
              "Kanton Bern" : [(3675033536,(47.26210075317295,7.168583438094979)), (33202504,(46.947313710211645, 7.444169998139135))],
              "Canton Ticino" :[(1479486535,(46.44094154118944,8.841014607372621))],
             }

swiss = "europe_switzerland.pbf"
name2pbfs = {
    "Kanton Aargau" : [ "Canton-Aargau-0.pbf", 
                        "Canton-Aargau-1.pbf",  ],
    "Kanton Appenzell Ausserrhoden" : [ "Canton-Appenzell Ausserrhoden-0.pbf" ],
    "Kanton Appenzell Innerrhoden" : [ "Canton-Appenzell Innerrhoden-0.pbf", 
                                       "Canton-Appenzell Innerrhoden-1.pbf", 
                                       "Canton-Appenzell Innerrhoden-2.pbf", 
                                       "Canton-Appenzell Innerrhoden-3.pbf", 
                                       #"Canton-Appenzell Innerrhoden-4.pbf"
                                      ],
    "Kanton Basel-Landschaft" : [ "Canton-Basel-Landschaft-0.pbf", 
                                  "Canton-Basel-Landschaft-1.pbf" ],
    "Kanton Basel-Stadt" : [ "Canton-Basel-Stadt-0.pbf" ],
    "Kanton Bern" : [ "Canton-Bern-0.pbf", 
                      "Canton-Bern-1.pbf", 
                      "Canton-Bern-2.pbf", 
                      "Canton-Bern-3.pbf" ],
    "Canton de Fribourg" : [ "Canton-Fribourg-0.pbf", 
                             "Canton-Fribourg-1.pbf", 
                             "Canton-Fribourg-2.pbf", 
                             "Canton-Fribourg-3.pbf", 
                             "Canton-Fribourg-4.pbf", 
                             "Canton-Fribourg-5.pbf" ],
    "Canton de Genève" : [ "Canton-Genève-0.pbf", 
                           "Canton-Genève-1.pbf", 
                           "Canton-Genève-2.pbf" ],
    "Kanton Glarus" : [ "Canton-Glarus-0.pbf" ],
    "Kanton Graubünden" : [ "Canton-Graubünden-0.pbf" ],
    "Kanton Luzern" : [ "Canton-Luzern-0.pbf" ],
    "Canton de Neuchâtel" : [ "Canton-Neuchâtel-0.pbf" ],
    "Kanton Nidwalden" : [ "Canton-Nidwalden-0.pbf" ],
    "Kanton Obwalden" : [ "Canton-Obwalden-0.pbf", 
                          "Canton-Obwalden-1.pbf" ],
    "Kanton Schaffhausen" : [ "Canton-Schaffhausen-0.pbf", 
                              "Canton-Schaffhausen-1.pbf", 
                              "Canton-Schaffhausen-2.pbf" ],
    "Kanton Schwyz" : [ "Canton-Schwyz-0.pbf" ],
    "Kanton Solothurn" : [  "Canton-Solothurn-0.pbf", 
                            "Canton-Solothurn-1.pbf", 
                            "Canton-Solothurn-2.pbf", 
                            "Canton-Solothurn-3.pbf" ],
    "Kanton St. Gallen" : [ "Canton-St Gallen-0.pbf", 
                            "Canton-St Gallen-1.pbf" ],
    "Kanton Thurgau" : [ "Canton-Thurgau-0.pbf", 
                         "Canton-Thurgau-1.pbf" ],
    "Kanton Uri" : [ "Canton-Uri-0.pbf" ],
    "Canton de Vaud" : [ "Canton-Vaud-0.pbf", 
                         "Canton-Vaud-1.pbf" ],
    "Kanton Zug" : [ "Canton-Zug-0.pbf" ],
    "Kanton Zürich" : [ "Canton-Zürich-0.pbf" ],
    "Canton Ticino" : [ "Canton-Ticino-0.pbf" ],
    "Canton du Jura" : [ "Canton-Jura-0.pbf" ],
    "Kanton Wallis" : [ "Canton-Valais-0.pbf" ],
}

def findPbfs(name):
    return name2pbfs[name]

def startGraphHopper(pbf):
    return subprocess.Popen(["./graphhopper.sh",
                             "-a", "web",
                             "-i", "../STUF/swissBoundaries/Cantons/%s" % pbf,
                             "-o", "%s-gh" % pbf],
                            cwd="/home/sponcec3/DEVEL/graphhopper")

def extractWeights(pbf):
    weights = {}
    # start graphhopper server in a separate process
    p = startGraphHopper(pbf)
    # wait a bit that it's running
    time.sleep(5)
    nb = 0
    # build weights
    for an in range(len(pointIds)):
        if pointIds[an] not in weights:
            weights[pointIds[an]] = {}
        for bn in range(len(pointIds)):
            if an == bn: continue
            w = getWeight(pointCoords[an],pointCoords[bn])
            # ignore impossible paths (can happen when cantons are non connex)
            if w:
                if pointIds[bn] in weights[pointIds[an]]:
                    # we may have a shorter route outside the canton !
                    w = min(w, weights[pointIds[an]])
                    print(w, weights[pointIds[an]])
                nb += 1
                print (pointIds[an],pointIds[bn],w)
                weights[pointIds[an]][pointIds[bn]] = w
    print("%s done, %d routes computed, now cleaning" % (name, nb))
    p.terminate()
    return weights


weights = {}
for name in points:
    print("starting %s, %d points. Please launch graphhopper" % (name, len(points[name])))
    pbfnames = findPbfs(name)
    print("Found %d pbfs" % len(pbfnames))
    # collect all points for this canton, including additions
    # note that we keep first point of each segment
    pointIds = [a for a,b in points[name]]
    pointCoords = [ (allNodes[a]['lat'], allNodes[a]['lon']) for a in pointIds]
    # cleanup to get less points
    pointIds, pointCoords = cleanup(name, pointIds, pointCoords)
    # add additional points
    if name in additions:
        for id, coords in additions[name]:
            pointIds.append(id)
            pointCoords.append(coords)
    for pbf in pbfnames:
        # extract all weights within the canton
        nw = extractWeights(pbf)
        # extract same weights on whole switzerland
        sw = extractWeights(swiss)
        # keep only those shorter through the canton
        nb = 0
        for a in nw:
            for b in nw[a]:
                if a in sw and b in sw[a] and sw[a][b] >= nw[a][b]:
                    w = nw[a][b]
                    if a not in weights:
                        weights[a] = {}
                    if b in weights[a]:
                        w = min(w, weights[a][b])
                    weights[a][b] = w
                    nb += 1
        print("%s routes left after cleaning" % nb)

fh = open("weights.pkl", 'wb')
pickle.dump(weights, fh)
fh.close()
