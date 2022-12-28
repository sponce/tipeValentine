import numpy as np
import random, operator
import pandas as pd
import matplotlib.pyplot as plt

class geoData:
    '''
    class describing the geography on which we will work
    Consists of :
       - pointsPerCanton is a dictionnary with keys being the canton names
         each value is a list of pairs id of point, id of way
       - fixedPoints is a dict of fixed points to go through
         each value is a pair with point id and name of the canton you're in
       - distances is a dict of dict giving the distance between 2 points
       - borders is a dict of dict giving the set of points on the border between 2 cantons
       - cantonGraph (computed from the rest) is a dict of dict giving for
         each pair of cantons lists of possible intermediate cantons to go
         through to reach the later from the former. Only shortest path are
         listed. Each entry is a list of lists
       - (unused) allNodes is a dict with key the id of the nodes and value a dict with node data
         out of which id, lon and lat
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
                townC = self.fixedPoints[c][1]
                if n == 0 or cantons[n-1] != townC:
                    extendedCantons.append(townC)
            extendedCantons.append(c)
            if isTown:
                if n!= len(cantons)-1 and cantons[n+1] != townC:
                    extendedCantons.append(townC)
        route = []
        # add extra cantons when cantons do not touch each other
        finalList = [[]]
        if extendedCantons[1] not in self.fixedPoints or self.fixedPoints[extendedCantons[1]][1] != extendedCantons[0]:
            finalList = [[extendedCantons[0]]]
        for n in range(1, len(extendedCantons)):
            c1 = extendedCantons[n-1]
            c2 = extendedCantons[n]
            # if we got 2 cantons, add extra ones when needed
            if c1 not in self.fixedPoints and c2 not in self.fixedPoints:
                newFinalList = []
                for f in finalList:
                    for ext in self.cantonsGraph[c1][c2]:
                        newFinalList.append(f + ext)
                finalList = newFinalList
            # add new canton/town to all lists
            newFinalList = []
            for fin in finalList:
                newFinalList.append(fin+[c2])
            finalList = newFinalList
        return finalList

    def _addFixedPointToRoute(self, route, point):
        mind = 999999999
        npath = []
        for path, d in route:
            #print ('X', path, point)
            if path[-1] != point:
                d = d + self.distances[path[-1]][point]
                p = path + [point]
            else:
                p = path
            if d < mind:
                mind = d
                npath = p
        return [(npath, mind)]

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
        # compute best route for each list of cantons
        mind = 9999999999999
        minPath = []
        for l in lists :
            # initialize routes with points in first canton or town
            if l[0] in self.fixedPoints:
                route = [([l[0]],0)]
            else:
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

class Route:
    '''
    Object holding a route, that is a list of places the route goes through
    '''
    def __init__(self, data, cantons):
        self.cantons = cantons[:]
        self.path, self.distance = data.bestRoutesFromCantonList(cantons)
        self.fitness = 1000 / float(self.distance) if self.distance else 999999
    def routeFitness(self):
        return self.fitness
    def routeDistance(self):
        return self.distance
    def __repr__(self):
        return "%s d=%.3f f=%.3f" % (str(self.cantons), self.distance, self.fitness)
    def breed(self, data, other):
        geneA = int(random.random() * len(self.cantons))
        geneB = int(random.random() * len(self.cantons))
        startGene = min(geneA, geneB)
        endGene = max(geneA, geneB)
        childP1 = self.cantons[startGene:endGene+1]
        childP2 = [item for item in other.cantons if item not in childP1]
        return Route(data, childP1 + childP2)
    def mutate(self, data, mutationRate):
        ncs = self.cantons[:]
        for swapped in range(len(ncs)):
            if(random.random() < mutationRate):
                swapWith = int(random.random() * len(ncs))
                c1 = ncs[swapped]
                c2 = ncs[swapWith]
                ncs[swapped] = c2
                ncs[swapWith] = c1
        return Route(data, ncs)


def initialPopulation(data, popSize):
    '''creates a population of random routes given a set of cantons'''
    # list fixedPoints
    cantons = list(data.fixedPoints.keys())
    # add all cantons, except the ones containing fixed points
    cantons.extend(list(set(data.pointsPerCanton.keys())-set([c for id,c in data.fixedPoints.values()])))
    population = []
    for i in range(0, popSize):
        random.shuffle(cantons)
        population.append(Route(data, cantons))
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

def breedPopulation(data, matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))
    for i in range(0,eliteSize):
        children.append(matingpool[i])    
    for i in range(0, length):
        child = pool[i].breed(data, pool[len(matingpool)-i-1])
        children.append(child)
    return children

def mutatePopulation(data, population, mutationRate):
    mutatedPop = []    
    for ind in range(0, len(population)):
        mutatedInd = population[ind].mutate(data, mutationRate)
        mutatedPop.append(mutatedInd)
        mutatedPop.append(population[ind])            
    return mutatedPop

def nextGeneration(data, currentGen, eliteSize, mutationRate):
    popRanked = rankRoutes(currentGen)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(data, matingpool, eliteSize)
    nextGeneration = mutatePopulation(data, children, mutationRate)
    return nextGeneration

def geneticAlgorithm(data, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(data, popSize)
    print(pop)
    print("Initial distance: " + str(1000 / rankRoutes(pop)[0][1]))
    for i in range(0, generations):
        pop = nextGeneration(data, pop, eliteSize, mutationRate)
        print(pop)
    print("Final distance: " + str(1000 / rankRoutes(pop)[0][1]))
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
