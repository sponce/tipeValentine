#
# Input data format :
#   each node is a triplet lat,lon,bitmask
#   nodes are stored in a dictionnary, keyed by their id
#   a dictionary of dictionaries gives the oriented weight of each route between 2 connected nodes
# Note that the weight is the weight from the reverse route,
# as we will build the route backwards
#
# Each bit of the bitmask is either a node or a canton
#   - in case of node, only that node has the bit set
#   - in case of canton, all nodes in the canton have it
#
# During the algo, routes is a list of currently investigated routes
# It is a tuple :
#   (curNode, prevNodes, length, bitmask)
#   where bitmask gives the list of all nodes/countries visited so far
#
# a list of bestRoutes is maintained, under the form of a dictionnary keyed
# by the current destination and containing dictionnaries keyed by the bitmask 
# and containing the current best route for this combinaison
#

import pickle
import matplotlib.pyplot as plt
import json

fh = open("InputNodes.pkl", 'rb')
points, additions, allNodes = pickle.load(fh)

# first create bit sets for each canton and additional point
cur = 1
bitsets = {}
cantonsWithPoints = set([additions[name][1] for name in additions])
for name in points:
    if name in cantonsWithPoints or name == "Kanton Aargau" or name == "Kanton Basel-Landschaft" or name == "Canton de Vaud" or name == "Kanton Luzern" or name == "Kanton Graubünden": # and name != "Canton de Genève" and name != "Canton Ticino":
        bitsets[name] = 0
    else:
        bitsets[name] = cur
        cur *= 2
for name in additions:
    id, canton = additions[name]
    bitsets[id] = cur
    cur *= 2
for name in additions:
    id, canton = additions[name]
    print (name, canton, hex(bitsets[id]))
completeRouteMask = cur-1
print (bitsets, cur, completeRouteMask, bin(completeRouteMask).count('1'))

# build the table to nodes
nodes = {}
for name in points:
    for id in [a for a,b in points[name]]:
        bs = bitsets[name]
        if id in nodes:
            nodes[id][2] = nodes[id][2] | bs
        else:
            nodes[id] = [allNodes[id]['lat'], allNodes[id]['lon'], bs]
for name in additions:
    id, canton = additions[name]
    nodes[id] = [allNodes[id]['lat'], allNodes[id]['lon'], bitsets[id]]

# load the weightsTable
fh = open("weights.pkl", 'rb')
weights = pickle.load(fh)

# initial setup (reverse start from Bern)
routes = {33202504:{bitsets[33202504]:(33202504, [], 0, bitsets[33202504])}}
print ("initial route", routes)
bestRoutes = {}
bestRoute = ()
bestLength = 99999999999999999999999999

def checkAndAddRoute(node, prevNodes, length, bitmask):
    global newRoutes, bestRoutes, bestRoute, bestLength
    # do not keep routes already longer than best complete one
    if length < bestLength:
        # check we do not have a shorter route with same goal and bitmask
        if node not in bestRoutes:
            bestRoutes[node] = {}
        if bitmask not in bestRoutes[node] or bestRoutes[node][bitmask][2] > length:
            # yes, so keep the route, except if it's complete
            route = (node, prevNodes, length, bitmask)
            #print ("NB", node, bitmask, length, prevNodes)
            bestRoutes[node][bitmask] = route
            if bitmask != completeRouteMask :
                if node not in newRoutes: newRoutes[node] = {}
                newRoutes[node][bitmask] = route
            else:
                bestLength = length
                bestRoute  = (prevNodes + [node])
                print ("New best, complete route", length, bestRoute)

def buildNewRoutes():
    global newRoutes
    newRoutes = {}
    for curNode in routes:
        for bitmask in routes[curNode]:
            prevNodes = routes[curNode][bitmask][1]
            length =  routes[curNode][bitmask][2]
            if curNode in weights:
                for newDest in weights[curNode]:
                    if newDest not in nodes: continue
                    #if not prevNodes:
                    newPrevNodes = prevNodes+[curNode]
                    #else:
                    #    newPrevNodes = prevNodes
                    newLength = length+weights[curNode][newDest]
                    newBitmask = bitmask|nodes[newDest][2]
                    checkAndAddRoute(newDest, newPrevNodes, newLength, newBitmask)

def disp(name, color, ax):
    data = json.load(open("../swissBoundaries/Cantons/%s"%name,'r'))
    for feat in data['features']:
        coords = feat['geometry']['coordinates']
        for pol in coords:
            x = [c[0] for c in pol]
            y = [c[1] for c in pol]
            ax.plot(x,y,color=color)

#cols = [ 'red', 'blue', 'green', 'orange', 'black', 'pink', 'gray' ]

def displayNewRoutes(n):
    rs = {}
    c = 0
    for node in newRoutes:
        routes = []
        bms = []
        for bm in newRoutes[node]:
            #print (hex(bm), bin(bm).count("1"))
            #for bz in bms:
            #    if bm&bz==bm:
            #        print ("%x < %x, %d >? %d" % (bm, bz, newRoutes[node][bm][2], newRoutes[node][bz][2]))
            bms.append(bm)
            pnodes = newRoutes[node][bm][1]
            routes.append(pnodes)
            bms.append(bm)
        c = c + 1
        #if c > 3: break
        print (node, routes[0])
        ax = plt.subplot()
        plotted = []
        disp('swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.geojson', 'gray', ax)
        for pnodes in routes:
            if node not in plotted:
                plotted.append(node)
                ax.plot(allNodes[node]['lon'], allNodes[node]['lat'], 'gx')
            nodes = pnodes + [node]
            for index in range(len(pnodes)):
                ax.plot((allNodes[nodes[index]]['lon'], allNodes[nodes[index+1]]['lon']),
                        (allNodes[nodes[index]]['lat'], allNodes[nodes[index+1]]['lat'])#,
                        #cols[index]
                        )
            break
        plt.show()

def keepShortRoutes(rs, n):
    #n = max([bin(rs[node][bm][3]).count('1') for node in rs for bm in rs[node]])
    #allRoutes = [rs[node][bm] for node in rs for bm in rs[node]]
    #sorted(allRoutes, key=lambda r: r[2]/(bin(r[3]).count('1')**2))
    #kept = allRoutes[:200]
    kept = [rs[node][bm] for node in rs for bm in rs[node] if bin(rs[node][bm][3]).count('1')>n-3 ]
    if len(kept) > 2000000:
        sorted(kept, key=lambda r: r[2]-200000000*(bin(r[3]).count('1')))
        kept = kept[:1000000]
    #print (kept[0][2], hex(kept[0][3]), kept[10][2], hex(kept[10][3]), kept[20][2], hex(kept[20][3]))
    res = {}
    for node, pnodes, l, bm in kept:
        if node not in res: res[node] = {}
        res[node][bm] = (node, pnodes, l, bm)
    return res
        
# loop until all routes are complete or gone
n = 0
while len(routes.keys()) > 0:
    print (n)
    buildNewRoutes()
    if len(newRoutes) == 0: break
    nb = sum([len(newRoutes[n].keys()) for n in newRoutes])
    print ("New routes : %d, nbCantones=%d" % (nb, max([bin(newRoutes[node][bm][3]).count('1') for node in newRoutes for bm in newRoutes[node]])))
    #if n == 30: displayNewRoutes(n)
    if nb > 20000:
        routes = keepShortRoutes(newRoutes, n)
    else:
        routes = newRoutes
    n += 1
    if n > 40: break

# keep only complete routes from the bestRoutes and find best one
finalRoutes = []
for node in bestRoutes:
    #print ([hex(d) for d in bestRoutes[node]])
    if completeRouteMask in bestRoutes[node]:
        node, prevNodes, length, bitmask = bestRoutes[node][completeRouteMask]
        nodes = prevNodes + [node]
        finalRoutes.append((nodes, length))
        if length < bestLength:
            bestLength = length
            bestRoute = prevNodes + [node]

# some printing
print ("Found %d complete routes" % len(finalRoutes))
for nodes, length in finalRoutes:
    print (length, nodes)

if len(finalRoutes) == 0:
    for node in bestRoutes:
        for mask in bestRoutes[node]:
            if bin(mask).count('1') >= 26:
                print (hex(mask), hex(completeRouteMask-mask))
        
    
# best route
print ("\nBest route is")
print (bestLength, bestRoute)
