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

def createRoute(cityList):
    route = random.sample(cityList, len(cityList))
    return route

def breed(parent1, parent2):
    fils = []
    filsP1 = []
    filsP2 = []
    
    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))
    while geneA==geneB:
        geneB = int(random.random() * len(parent1))
    #print('gene',geneA,geneB)
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        filsP1.append(parent1[i])

    clusFilsP1 = [nodeToCluster[item] for item in filsP1]
    filsP2 = [item for item in parent2 if nodeToCluster[item] not in clusFilsP1]

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
    for swapped in range(len(route)):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(route))
            #print('mutate',swapped,swapWith)
            city1 = route[swapped]
            city2 = route[swapWith]
            
            route[swapped] = city2
            route[swapWith] = city1
        if random.random() < clusterMutationRate:
            # take another city in the same cluster
            clus = nodeToCluster[route[swapped]]
            #oldplace = route[swapped]
            #oldL = Fitness(route).distance
            route[swapped] = random.choice(clusters[clus])
            #print(oldplace, oldL, route[swapped], Fitness(route).distance)
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
    route = []
    for c in clusters:
        if len(c) > 0:
            route.append(random.choice(c))
    return random.sample(route, len(route))

# load data from SmallProblem
with open("SwissSimpleGraph.pkl", 'rb') as file:
    ng, ncoords, clusters, nodeToCluster = pickle.load(file)
with open("SwissDistances.pkl", 'rb') as file:
    distances = pickle.load(file)
with open("CantonPolys.pkl", 'rb') as file:
    polys = list(pickle.load(file).values())

Citylist=ng.nodes()
totalsize=400
eliteSize=100
breedingExtraSize=100
population=[createRoute(clusters) for i in range(totalsize)]
n=2000
MeilleursChemins = []
nDisplay=1

for i in range (n):
    #print("S1", len(population))
    parcours_trie=Tri_Parcours(population)
    if len(MeilleursChemins) == 0 or parcours_trie[0][1] < MeilleursChemins[-1][1]:
        MeilleurChemin = (population[parcours_trie[0][0]].copy(), parcours_trie[0][1])
        MeilleursChemins.append(MeilleurChemin)
        print (MeilleurChemin)
    matingpool=selection(parcours_trie,eliteSize,totalsize)
    #print("S2", len(matingpool))
    new_pop=breedPopulation(matingpool, eliteSize, breedingExtraSize)
    #print("S3", len(new_pop))
    population=mutatePopulation (new_pop,0.04,0.2)



from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection

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
    
colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

fig, ax = plt.subplots()

for c in MeilleursChemins[-nDisplay:]:
    for n in range(len(clusters)):
        color = colors[n%len(colors)]
        networkx.draw_networkx_nodes(ng, ncoords, clusters[n], node_size=20, node_color=color)
        lightcolor = lighter(color)
        for poly in polys[n].polys:
            plot_polygon(ax, poly, color=lightcolor)
    pairRoute = list(networkx.utils.pairwise(c[0]))
    networkx.draw_networkx_edges(ng, ncoords, pairRoute, node_size=0, width=1)
    #for n in c[0]:
    #    networkx.draw_networkx_nodes(ng, ncoords, [n], node_size=40, node_color=colors[nodeToCluster[n]%len(colors)])    
    plt.show()
