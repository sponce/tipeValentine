import osmapi as osm
import pickle

fh = open("InputData.pkl", 'rb')
points, additions = pickle.load(fh)

api = osm.OsmApi()

n = 0
for name in points:
    n += len(points[name])
    print ("%s has %d real exits" % (name, len(points[name])))

allPoints = set([])
for name in points:
    for a,b in points[name]:
        allPoints.add(a)
print ("Total nb points : %d, from %d" % (len(allPoints), n))

allNodes = {}
count = 0
for n in allPoints:
    allNodes[n] = api.NodeGet(n)
    count+= 1
    if count%20 == 0: print (count)
for k,v in additions.items():
    allNodes[v[0]] = api.NodeGet(v[0])

fh = open("InputNodes.pkl", 'wb')
pickle.dump((points, additions, allNodes), fh)
fh.close()
