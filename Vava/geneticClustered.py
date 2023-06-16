import numpy as np,random,operator, matplotlib.pyplot as plt
from pylab import figure,plot,show
import pickle
import networkx
   
class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

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
        
    filsP2 = [item for item in parent2 if item not in filsP1]

    fils = filsP1 + filsP2
    return fils

def breedPopulation(matingpool, eliteSize, extraSize):
    print("BEF", len(matingpool))
    children = []
    length = len(matingpool) - eliteSize + extraSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0,eliteSize):
        children.append(matingpool[i])
    
    for i in range(0, min(length, len(pool))):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        #print('breeding',pool[i],pool[len(matingpool)-i-1],child)
        children.append(child)
    print("AFT", len(children))
    return children

def mutate(route, mutationRate):
    for swapped in range(len(route)):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(route))
            #print('mutate',swapped,swapWith)
            city1 = route[swapped]
            city2 = route[swapWith]
            
            route[swapped] = city2
            route[swapWith] = city1
    return route

def mutatePopulation(population, mutationRate):
    mutatedPop = []
    for route in range(0, len(population)):
        mutatedInd = mutate(population[route], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

def createRoute(clusters):
    # pick one city per cluster and randomize the order
    route = []
    for c in clusters:
        route.append(random.choice(c))
    return random.sample(route, len(route))

# load data from SmallProblem
with open("SmallPbSimpleGraph.pkl", 'rb') as file:
    ng, ncoords, clusters, nodeToCluster = pickle.load(file)
with open("SmallPbDistances.pkl", 'rb') as file:
    distances = pickle.load(file)

Citylist=ng.nodes()
totalsize=400
eliteSize=100
breedingExtraSize=100
population=[createRoute(clusters) for i in range(totalsize)]
n=80
MeilleurChemin = (0, 9999999)
for i in range (n):
    print("S1", len(population))
    parcours_trie=Tri_Parcours(population)
    if parcours_trie[0][1] < MeilleurChemin[1]:
        MeilleurChemin = (population[parcours_trie[0][0]].copy(), parcours_trie[0][1])
        print(MeilleurChemin[1], parcours_trie[0][1])
    matingpool=selection(parcours_trie,eliteSize,totalsize)
    print("S2", len(matingpool))
    new_pop=breedPopulation(matingpool, eliteSize, breedingExtraSize)
    print("S3", len(new_pop))
    population=mutatePopulation (new_pop,0.01)

colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
for n in range(len(clusters)):
    networkx.draw_networkx_nodes(ng, ncoords, clusters[n], node_size=20, node_color=colors[n%len(colors)])
pairRoute = list(networkx.utils.pairwise(MeilleurChemin[0]))
networkx.draw_networkx_edges(ng, ncoords, pairRoute, node_size=0, width=1)

plt.show()
