import numpy as np
import random, operator
import pandas as pd
import matplotlib.pyplot as plt


class Route:
    '''Object holding a route, that is a list of places the route goes through'''
    def __init__(self, data, cantons):
        self.places = data.createRouteFromCantonList(cantons)
        self.distance = 0
        for n in range(len(self.places)-1):
            self.distance += data.distances[self.places[n]][self.places[n+1]]
        self.fitness = 1 / float(self.distance) if self.distance else 999999
    def routeFitness(self):
        return self.fitness
    def routeDistance(self):
        return self.distance
    def __repr__(self):
        return "%s d=%.3f f=%.3f" % (str(self.places), self.distance, self.fitness)

class geoData:
    '''
    class describing the geography on which we will work
    Consists of :
       - pointsPerCanton is a dictionnary with keys being the canton names
         each value is a list of pairs id of point, id of way
       - fixedPoints is a dict of fixed points to go through
         each value is a pair with point id and name of the canton you're in
       - allNodes is a dict with key the id of the nodes and value a dict with node data
         out of which id, lon and lat
       - distances is a dict of dict giving the distance between 2 points
       - borders is a dict of dict giving the set of points on the border between 2 cantons
       - cantonGraph (omputed from the rest) is a dict of dict giving for
         each pair of cantons lists of possible intermediate cantons to go
         through to reach the later from the former. Only shortest path are
         listed. Each entry is a list of lists
    This class should be inherited from by actual instantiations which will fill
    all data from external source
    '''
    def __init__(self):
        for c1 in self.pointsPerCanton:
            self.cantonsGraph[c1] = {}
            self.cantonsGraph[c1][c1] = {}
            self._computeRoutes(c1, [(c2, []) for c2 in self.borders[c1]])

    def _computeRoutes(self, c1, rs):
        '''build a graph of cantons, where each entry gives a list of
           intermediates cantons to go from c1 to c2'''
        while len(rs) > 0:
            #print(self.cantonsGraph, rs)
            nrs = []
            for (c2, r) in rs:
                if c2 not in self.cantonsGraph[c1]:
                    self.cantonsGraph[c1][c2] = []
                self.cantonsGraph[c1][c2].append(r)
            for (c2, r) in rs:
                for c3 in self.borders[c2]:
                    #print (c2, c3, c3 not in self.cantonsGraph[c1])
                    if c3 not in self.cantonsGraph[c1]:
                        nrs.append((c3, r+[c2]))
            rs = nrs

    def amendCantonList(self, cantons):
        '''Amends a list of cantons and town so that a town is always surrounded
           by its canton in the list and 2 successive canton are always touching.
           When 2 cantons do not touch, extra cantons are added in between using
           the cantonsGraph. When several possibilities exist, ll of them are exercised
           So what is returned is actually a list of all possible lists
        '''
        extendedCantons = []
        # surround towns with their cantons in the original list
        for n in range(0, len(cantons)):
            c = cantons[n]
            isTown = c in self.fixedPoints
            if isTown:
                townC = fixed2Canton[c]
                if n == 0 or cantons[n-1] != townC:
                    extendedCantons.append(townC)
            extendedCantons.append(c)
            if isTown:
                if n!= len(cantons) and cantons[n+1] != townC:
                    extendedCantons.append(townC)
        route = []
        # add extra cantons when cantons do not touch each other
        finalList = [[]]
        if extendedCantons[1] not in self.fixedPoints or fixed2Canton[extendedCantons[1]] != extendedCantons[0]:
            finalList = [[extendedCantons[0]]]
        for n in range(1, len(extendedCantons)):
            c1 = extendedCantons[n-1]
            c2 = extendedCantons[n]
            newFinalList = []
            if c1 not in self.fixedPoints and c2 not in self.fixedPoints:
                for f in finalList:
                    for ext in self.cantonsGraph[c1][c2]:
                        newFinalList.append(f + ext)
            finalList = newFinalList
            newFinalList = []
            for fin in finalList:
                newFinalList.append(fin+[c2])
            finalList = newFinalList
        return finalList

    def createRouteFromCantonList(self, cantons):
        '''creates a route from a list of cantons. A route is a list of places
           the route goes through. it's basically using amendCantonList and
           picking places at random on the borders of cantons'''
        route = []
        cantons = self.amendCantonList(cantons)[0] # FIXME !!!
        for n in range(1, len(cantons)):
            c1 = cantons[n-1]
            if c1 in self.fixedPoints:
                route.append(c1)
                continue
            c2 = cantons[n]
            if c2 in self.fixedPoints:
                continue
            city = random.choice(self.borders[c1][c2])
            #print (city, c1, c2)
            route.append(city)
        return route

    def _addFixedPointToRoute(self, route, point):
        mind = 999999999
        npath = []
        for path, d in route:
            d = d + self.distances[path[-1]][point]
            if d < mind:
                mind = d
                npath = path
        return [(npath+[point], mind)]

    def _addCantonToRoute(self, route, canton):
        nRoute = []
        # compute best route for each point
        for p, way in self.pointsPerCanton[canton]:
            if p in self.fixedPoints: continue
            np = []
            mind = 999999999
            for path, d in route:
                if p == path[-1]:
                    mind = d
                    np = path
                    break
                else:
                    if p in self.distances[path[-1]]:
                        d = d + self.distances[path[-1]][p]
                        if d < mind:
                            mind = d
                            np = path+[p]
            nRoute.append((np, mind))
        return nRoute
        
    def _bestRoutesFromCantonList(self, remCantons, route):
        '''extends a route from a list of cantons/fixedPoints.
           A route is actually a list of pairs path, distance.
           Each path is itself a list of places and there is one for each place
           in the latest visited canton, being the shortest one to reach this
           place.
           This method will create a new set of paths adding the remaining cantons
           '''
        # cut recursivity in case no cantons remanining in the list
        if remCantons == []:
            return route
        nextPoint = remCantons[0]
        # case of a fixed point
        if nextPoint in self.fixedPoints:
            nRoute = self._addFixedPointToRoute(route, nextPoint)
        else:
            # no fixed point
            nRoute = self._addCantonToRoute(route, nextPoint)
        # Call ourself recursively for next cantons/fixedPoints in the list
        return self._bestRoutesFromCantonList(remCantons[1:], nRoute)

    def bestRoutesFromCantonList(self, cantons):
        '''
        return the best path for the given list of cantons and its distance
        '''
        # get full list of cantons/fixedPoints
        lists = self.amendCantonList(cantons)
        #print(lists)
        # compute best route for each list of cantons
        mind = 9999999999999
        minPath = []
        for l in lists :
            # initialize routes with points in first canton
            route = [([p], 0) for p,way in self.pointsPerCanton[l[0]]]
            # compute best routes to any point in last canton
            route = self._bestRoutesFromCantonList(l[1:], route)
            # keep only the shortest route of all
            bestPath, bestDist = sorted(route, key=operator.itemgetter(1))[0]
            # compare with best so far
            if bestDist < mind:
                minPath = bestPath
                mind = bestDist
        return minPath, mind
    
    def initialPopulation(self, popSize, cantons):
        '''creates a population of random routes given a set of cantons'''
        population = []
        for i in range(0, popSize):
            population.append(Route(self, cantons))
        return population

def rankRoutes(population):
    '''Ranks a populations of routes based on their fitness (1/length)'''
    fitnessResults = {}
    for i in range(0,len(population)):
        fitnessResults[i] = population[i].routeFitness()
    return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)

def selection(popRanked, eliteSize):
    '''Selects routes from a rankes populations, returning the set on
       indexes of the routes to keep.
       First keeps eliteSize routes (the best ones) and then randomly keeps
       some others with weights proportional to their fitness
    '''
    selectionResults = []
    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    maxFit = max([fitness for i, fitness in popRanked])
    for i in range(eliteSize, len(popRanked)):
        pick = maxFit*random.random()
        index, fitness = popRanked[i]
        if pick <= fitness:
            selectionResults.append(index)
    return selectionResults

def matingPool(population, selectionResults):
    matingpool = []
    for i in range(0, len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool

def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []
    
    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))
    
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])
        
    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child

def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0,eliteSize):
        children.append(matingpool[i])
    
    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        children.append(child)
    return children

def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))
            
            city1 = individual[swapped]
            city2 = individual[swapWith]
            
            individual[swapped] = city2
            individual[swapWith] = city1
    return individual

def mutatePopulation(population, mutationRate):
    mutatedPop = []
    
    for ind in range(0, len(population)):
        mutatedInd = mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

def nextGeneration(currentGen, eliteSize, mutationRate):
    popRanked = rankRoutes(currentGen)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutatePopulation(children, mutationRate)
    return nextGeneration

def geneticAlgorithm(population, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, population)
    print("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))
    
    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)
    
    print("Final distance: " + str(1 / rankRoutes(pop)[0][1]))
    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]
    return bestRoute

cityList = []

#for i in range(0,25):
#    cityList.append(City(x=int(random.random() * 200), y=int(random.random() * 200)))

def geneticAlgorithmPlot(population, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, population)
    progress = []
    progress.append(1 / rankRoutes(pop)[0][1])
    
    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)
        progress.append(1 / rankRoutes(pop)[0][1])
    
    plt.plot(progress)
    plt.ylabel('Distance')
    plt.xlabel('Generation')
    plt.show()

#geneticAlgorithmPlot(population=cityList, popSize=100, eliteSize=20, mutationRate=0.01, generations=500)
#pop = initialPopulation(3,baseRoute)
#print(pop)
#print("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))
