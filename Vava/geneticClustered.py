import numpy as np,random,operator, matplotlib.pyplot as plt
from pylab import figure,plot,show
import pickle
import networkx

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance =0
        for i in range(0, len(self.route)-1):
            fromCity = self.route[i]
            toCity = self.route[i + 1]
            self.distance += distances[fromCity][toCity]

def Tri_Parcours(population):
    M=[]
    for i in range (0,len(population)):
        M.append((i,Fitness(population[i]).distance))
    return sorted(M,key = lambda item: item[1]) #lambda =fonction (entrée= item et renvoie item[1])

def selection (parcours_trie,eliteSize,totalSize):
    selectionResults=[]
    cum_som=0
    tot_som=sum([item[1] for item in parcours_trie])
    for i in range(0, eliteSize):
        selectionResults.append(population[parcours_trie[i][0]])
        cum_som+=parcours_trie[i][1]
    for i in range(eliteSize, len(parcours_trie)):
        pick = random.random()
        cum_som+=parcours_trie[i][1]
        #print(i,pick,cum_som/tot_som)
        if pick >= cum_som/tot_som:
            selectionResults.append(population[parcours_trie[i][0]])
            if len(selectionResults) == totalSize: break
    return selectionResults

def breed(parent1, parent2):
    fils = []
    filsP1 = []
    filsP2 = []
    
    geneA = int(random.random() * (len(parent1)-1))
    geneB = int(random.random() * (len(parent1)-1))
    while geneA==geneB:
        geneB = int(random.random() * len(parent1))
    #print('gene',geneA,geneB)
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        filsP1.append(parent1[i])

    clusFilsP1 = [nodeToCluster[item] for item in filsP1]
    filsP2 = [item for item in parent2 if (nodeToCluster[item] not in clusFilsP1 or
                                           (item in protectedItems and item not in filsP1))]

    fils = filsP1 + filsP2
    return fils

def breedPopulation(matingpool, eliteSize, extraSize):
    #print("BEF", len(matingpool))
    children = []
    length = len(matingpool) - eliteSize + extraSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0,eliteSize):
        children.append(matingpool[i])
    
    for i in range(0, min(length, len(pool))):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        #print('breeding',pool[i],pool[len(matingpool)-i-1],child)
        children.append(child)
    #print("AFT", len(children))
    return children

def mutate(route, mutationRate, clusterMutationRate):
    for swapped in range(len(route)-1): # preserve bern as last point
        if(random.random() < mutationRate):
            swapWith = int(random.random() * (len(route)-1))
            #print('mutate',swapped,swapWith)
            city1 = route[swapped]
            city2 = route[swapWith]
            
            route[swapped] = city2
            route[swapWith] = city1
        if random.random() < clusterMutationRate and \
           route[swapped] not in protectedItems and \
           swapped > 0 and swapped < len(route)-2:
            # take best city in the same cluster
            clus = nodeToCluster[route[swapped]]
            i0 = route[swapped-1]
            i1 = route[swapped]
            i2 = route[swapped+1]
            dorig = distances[i0][i1] + distances[i1][i2]
            for nc in clusters[clus]:
                if nc != route[swapped]:
                    newd = distances[i0][nc] + distances[nc][i2]
                    if newd < dorig:
                        route[swapped] = nc
                        dorig = newd
        for other in range(swapped+2, min(swapped+6, len(route)-1)):
            # 2-opt
            i1 = route[swapped]
            i2 = route[swapped+1]
            j1 = route[other]
            j2 = route[other+1]
            gain = distances[i1][i2] + distances[j1][j2] - distances[i1][j1] - distances[i2][j2]
            if gain > 0:
                r = route[swapped+1]
                route[swapped+1] = route[other]
                route[other] = r
    return route

def mutatePopulation(population, mutationRate, clusterMutationRate):
    mutatedPop = []
    for route in range(0, len(population)):
        mutatedInd = mutate(population[route], mutationRate, clusterMutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

def createRoute(clusters):
    # pick one city per cluster and randomize the order
    # make sure Bern is last
    route = []
    for c in clusters:
        if len(c) > 3:
            route.append(random.choice(c))
        else:
            for n in c:
                if n != bern:
                    route.append(n)
    return random.sample(route, len(route)) + [bern]

# load data from SmallProblem
print("Loading data...")
with open("SwissDiGraph.pkl", 'rb') as file:
    g, coords, _, _, osmidToNode = pickle.load(file)
with open("SwissSimpleGraph.pkl", 'rb') as file:
    ng, ncoords, clusters, nodeToCluster = pickle.load(file)
with open("SwissDistances.pkl", 'rb') as file:
    distances = pickle.load(file)
with open("CantonPolys.pkl", 'rb') as file:
    polys = list(pickle.load(file).values())

bern = osmidToNode[33202504]
Citylist=ng.nodes()
totalsize=400
eliteSize=100
breedingExtraSize=100
population=[createRoute(clusters) for i in range(totalsize)]
n=500
MeilleurChemin = None
nDisplay=1
protectedItems = []
for c in clusters:
    if len(c) < 4:
        protectedItems.extend(c)

print("Longueur du plus court chemin pour l'instant :")
for i in range (n):
    #print("S1", len(population))
    parcours_trie=Tri_Parcours(population)
    if MeilleurChemin is None or parcours_trie[0][1] < MeilleurChemin[1]:
        MeilleurChemin = (population[parcours_trie[0][0]].copy(), parcours_trie[0][1])
        print ("%f km" % (MeilleurChemin[1]/1000))
    matingpool=selection(parcours_trie,eliteSize,totalsize)
    #print("S2", len(matingpool))
    new_pop=breedPopulation(matingpool, eliteSize, breedingExtraSize)
    #print("S3", len(new_pop))
    population=mutatePopulation (new_pop,0.015,0.1)


from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.colors

# Plots a Polygon to pyplot `ax`
def plot_polygon(ax, poly, **kwargs):
    path = Path.make_compound_path(
        Path(np.asarray(poly.exterior.coords)[:, :2]),
        *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])
    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)    
    ax.add_collection(collection, autolim=True)


def lighter(hex_color, perc=0.7):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    rgb_hex = [int(hex_color[x:x+2], 16) for x in [1, 3, 5]]
    new_rgb_int = [c + int(perc*(255-c)) for c in rgb_hex]
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])

# Prepare figure and colors  
colors = [matplotlib.colors.to_hex(plt.cm.tab20(i)) for i in range(20)]
fig, ax = plt.subplots()

# draw all cantons in light colors
for n in range(len(clusters)):
    color = colors[n%len(colors)]
    # draw cantons
    lightcolor = lighter(color)
    for poly in polys[n].polys:
        plot_polygon(ax, poly, color=lightcolor)
# draw main nodes
for node in MeilleurChemin[0]:
    color = colors[nodeToCluster[node]%len(colors)]
    networkx.draw_networkx_nodes(ng, ncoords, [node], node_size=20, node_color=color)
# draw path
route = [MeilleurChemin[0][0]]
pairRoute = list(networkx.utils.pairwise(MeilleurChemin[0]))
for a,b in pairRoute:
    route.extend(networkx.shortest_path(g, a, b)[1:])
pairRoute = list(networkx.utils.pairwise(route))
networkx.draw_networkx_edges(g, coords, pairRoute, node_size=0, width=2, arrows=False)
plt.show()

# convert back to lat, lon from UTM data
print("Converting to gpx and adding elevation")
import geopandas as gpd
x = []
y = []
for p in route:
    lon, lat = coords[p]
    x.append(lon)
    y.append(lat)
utm="+proj=utm +zone=32 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
wgs84="EPSG:4326"
geometry = gpd.points_from_xy(x, y, crs=utm)
geo = geometry.to_crs(wgs84)

# save gpx track
with open('solution.gpx', 'w') as f:
  f.write('''<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>SUCH</name>
    <trkseg>''')
  for p in geo:
    f.write('      <trkpt lat="%f" lon="%f"></trkpt>' % (p.y, p.x))
  f.write('''    </trkseg>
  </trk>
</gpx>''')

# add ekevation to the gpx track
import srtm
import gpxpy
gpx = gpxpy.parse(open('solution.gpx'))
elevation_data = srtm.get_data()
elevation_data.add_elevations(gpx)
with open('solution.ele.gpx', 'w') as f:
    f.write(gpx.to_xml())

