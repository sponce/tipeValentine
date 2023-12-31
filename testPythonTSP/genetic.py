import numpy as np,random,operator, matplotlib.pyplot as plt
from pylab import figure,plot,show
   
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
            self.distance+= fromCity.distance(toCity)

def Tri_Parcours(population):
    M=[]
    for i in range (0,len(population)):
        M.append((i,Fitness(population[i]).distance))
    return sorted(M,key = lambda item: item[1]) #lambda =fonction (entrée= item et renvoie item[1])

def selection (parcours_trie,eliteSize):
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

def breedPopulation(matingpool, eliteSize):
    children = matingpool.copy()
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0,eliteSize):
        children.append(matingpool[i])
    
    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        #print('breeding',pool[i],pool[len(matingpool)-i-1],child)
        children.append(child)
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

def createRoute(cityList):
    route = random.sample(cityList, len(cityList))
    return route

#L=[1,2,3,4,5]
#print(createRoute (L))

Citylist=[City(1,2),City(3,6),City(5,4),City(2,4),City(3,2),City(3,8),City(9,7),City(7,2),City(0,5),City(20,12)]
population=[createRoute(Citylist) for i in range(40)]
eliteSize=10
n=80
MeilleurChemin = (0, 9999999)
for i in range (n):
    parcours_trie=Tri_Parcours(population)
    if parcours_trie[0][1] < MeilleurChemin[1]:
        MeilleurChemin = (population[parcours_trie[0][0]].copy(), parcours_trie[0][1])
        print(MeilleurChemin[1], parcours_trie[0][1])
    matingpool=selection(parcours_trie,eliteSize)
    #print(matingpool)
    new_pop=breedPopulation(matingpool, eliteSize)
    #print(new_pop)
    population=mutatePopulation (new_pop,0.01)

def affiche(Chemin):
    figure()
    lx=[k.x for k in Chemin]
    ly=[k.y for k in Chemin]
    plot(lx,ly,color='black',marker='s')
    plot(Chemin[0].x,Chemin[0].y,color='blue',marker='o')
    show ( )
affiche(MeilleurChemin[0])
