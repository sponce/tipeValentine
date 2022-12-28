from geneticStuf import *

class testData(geoData) :
    '''
    test data set
    5 cantons with following layout :
       A - B - C
         D - E - F
    each canton has a fixed point (resp a, b, c, d and e)
    and border places are called ab1 or be3 for example
    '''
    def __init__(self):
        self.fixedPoints = {
            'a' : (100, 'A'),
            'b' : (200, 'B'),
            'c' : (300, 'C'),
            'd' : (400, 'D'),
            'e' : (500, 'E'),
            'f' : (600, 'F')
        }
        self.borders = {
            'A' : {
                'B' : [ 121, 122, 123 ],
                'D' : [ 141, 142, 143 ],
            },
            'B' : {
                'A' : [ 121, 122, 123 ],
                'C' : [ 231, 232, 233 ],
                'D' : [ 241, 242, 243 ],
                'E' : [ 251, 252, 253 ],
            },
            'C' : {
                'B' : [ 231, 232, 233 ],
                'E' : [ 351, 352, 353 ],
                'F' : [ 361, 362, 363 ],
            },
            'D' : {
                'A' : [ 141, 142, 143 ],
                'B' : [ 241, 242, 243 ],
                'E' : [ 451, 452, 453 ],
            },
            'E' : {
                'B' : [ 251, 252, 253 ],
                'C' : [ 351, 352, 353 ],
                'D' : [ 451, 452, 453 ],
                'F' : [ 561, 562, 563 ],
            },
            'F' : {
                'C' : [ 361, 362, 363 ],
                'E' : [ 561, 562, 563 ]
            }
        }
        self.pointsPerCanton = {}
        self.distances = {}
        self.cantonsGraph = {}
        for c in self.borders:
            self.pointsPerCanton[c] = []
            for c2 in self.borders[c]:
                for p in self.borders[c][c2]:
                    self.pointsPerCanton[c].append((p, 0))
        for c1 in self.borders:
            d = ord(c1)-ord('A')+1
            for c2 in self.borders[c1]:
                for p1 in self.borders[c1][c2]:
                    if p1 not in self.distances:
                        self.distances[p1] = {}
                    for c3 in self.borders[c1]:
                        for p2 in self.borders[c1][c3]:
                            if p1 != p2:
                                self.distances[p1][p2] = d
        for p in self.fixedPoints:
            if p not in self.distances:
                self.distances[p] = {}
            id, c = self.fixedPoints[p]
            for p2, way in self.pointsPerCanton[c]:
                self.distances[p][p2] = 0.5
                if p2 not in self.distances:
                    self.distances[p2] = {}
                self.distances[p2][p] = 0.5
        super().__init__()

data = testData()

def test_computeRoute():
    assert data.cantonsGraph['A']['B'] == [[]]
    assert data.cantonsGraph['A']['C'] == [['B']]
    assert data.cantonsGraph['A']['E'] == [['B'],['D']]
    assert data.cantonsGraph['A']['E'] == [['B'],['D']]
    assert data.cantonsGraph['A']['F'] == [['B','C'],['B','E'],['D','E']]

def test_amendCantonList():
    assert data.amendCantonList(['A', 'C']) == [['A', 'B', 'C']]
    assert data.amendCantonList(['A', 'E']) == [['A', 'B', 'E'], ['A', 'D', 'E']]
    assert data.amendCantonList(['A', 'F']) == [['A', 'B', 'C', 'F'], ['A', 'B', 'E', 'F'], ['A', 'D', 'E', 'F']]
    assert data.amendCantonList(['a', 'b']) == [['a', 'A', 'B', 'b']]
    assert data.amendCantonList(['a', 'D', 'e']) == [['a', 'A', 'D', 'E', 'e']]
    assert data.amendCantonList(['a', 'A', 'a']) == [['a', 'A', 'a']]

ABRoutes = [[121],[122],[123]]
ACRoutes = [[121,231], [121,232], [121,233],
            [122,231], [122,232], [122,233],
            [123,231], [123,232], [123,233]]
AERoutes = [[121,251], [121,252], [121,253],
            [122,251], [122,252], [122,253],
            [123,251], [123,252], [123,253],
            [141,451], [141,452], [141,453],
            [142,451], [142,452], [142,453],
            [143,451], [143,452], [143,453]]

def test_addFixedPointToRoute():
    assert data._addFixedPointToRoute([([121],0), ([122],0), ([141],0)], 'a') == [([121, 'a'], 0.5)]

BRoutes = [([121], 0), ([122], 0), ([141, 123], 1), ([121, 231], 2), ([121, 232], 2), ([121, 233], 2), ([121, 241], 2), ([121, 242], 2), ([121, 243], 2), ([121, 251], 2), ([121, 252], 2), ([121, 253], 2)]
    
def test_addCantonToRoute():
    assert data._addCantonToRoute([([121],0), ([122],0), ([141],0)], 'B') == BRoutes
    
def test_bestRoutesFromCantonList_int():
    assert data._bestRoutesFromCantonList([], [([121],0)]) == [([121],0)]
    assert data._bestRoutesFromCantonList(['a'], [([121],0)]) == [([121,'a'],0.5)]
    assert data._bestRoutesFromCantonList(['B'], [([121],0), ([122],0), ([141],0)]) == BRoutes
    assert data._bestRoutesFromCantonList(['B','b'], [([121],0), ([122],0), ([141],0)]) == [([121, 'b'], 0.5)]
    assert data._bestRoutesFromCantonList(['a', 'A', 'B','b'], [([121],0), ([122],0), ([141],0)]) == [([121, 'a', 121, 'b'], 1.5)]
    assert data._bestRoutesFromCantonList(['B','C','F','f'], [([121],0), ([122],0), ([141],0)]) == [([121, 231, 361, 'f'], 5.5)]
    assert data._bestRoutesFromCantonList(['a', 'A', 'D', 'E', 'e'], [([121],0)]) == [([121, 'a', 121, 241, 251, 'e'], 5.5)]
    print('ST')
    assert data._bestRoutesFromCantonList(['a', 'A'], [(['a'],0)]) == [(['a', 121], .5), (['a', 122], .5), (['a', 123], .5), (['a', 141], .5), (['a', 142], .5), (['a', 143], .5)]

def test_bestRoutesFromCantonList():
    assert data.bestRoutesFromCantonList(['A','F']) == ([121, 231, 361], 5)
    assert data.bestRoutesFromCantonList(['A','D','F']) == ([141, 451, 561], 9)
    assert data.bestRoutesFromCantonList(['a','b']) ==  (['a', 121, 'b'], 1.)
    assert data.bestRoutesFromCantonList(['a','e']) ==  (['a', 121, 251, 'e'], 3.0)
    assert data.bestRoutesFromCantonList(['a','A']) ==  (['a', 121], 0.5)

def test_bestRoutesFromCantonList_speed():
    class largeData(geoData):
        def __init__(self):
            # let's create a large data set with n cantons touching each other in a line
            # and p points on each border. On top we'll have q fixed points in each canton
            n = 50
            p = 50
            q = 10
            # for ids, we'll use 10^6*c1+10^3*c2+border for borders (c1<c2)
            # and same for fixedPoints with c2 = n
            def id(point, c1, c2=n):
                return 1000000*c1+1000*c2+point
            self.fixedPoints = {}
            for ni in range(n):
                for qi in range(q):
                    self.fixedPoints["fp%d-%d" % (ni, qi)] = (id(qi,ni), "C%d" % ni);
            self.borders = {}
            for n1 in range(n):
                c1 = "C%d" % n1
                self.borders[c1] = {}
            self.pointsPerCanton = {}
            self.distances = {}
            self.cantonsGraph = {}
            self.pointsPerCanton["C0"] = []
            for n1 in range(n-1):
                c1 = "C%d" % n1
                n2 = n1+1
                c2 = "C%d" % n2
                self.pointsPerCanton[c2] = []
                self.borders[c1][c2] = [id(pi, n1, n2) for pi in range(p)]
                self.borders[c2][c1] = [id(pi, n1, n2) for pi in range(p)]
                self.pointsPerCanton[c1].extend([(id(pi, n1, n2), 0) for pi in range(p)])
                self.pointsPerCanton[c2].extend([(id(pi, n1, n2), 0) for pi in range(p)])
            for n1 in range(n):
                c1 = "C%d" % n1
                lc = []
                if n1 > 0: lc.append(n1-1)
                if n1 < n-1: lc.append(n1+1)
                for n2 in lc:
                    c2 = "C%d" % n2
                    for p1 in self.borders[c1][c2]:
                        if p1 not in self.distances:
                            self.distances[p1] = {}
                        for c3 in self.borders[c1]:
                            for p2 in self.borders[c1][c3]:
                                if p1 != p2:
                                    self.distances[p1][p2] = n1
            for p in self.fixedPoints:
                if p not in self.distances:
                    self.distances[p] = {}
                id, c = self.fixedPoints[p]
                for p2, way in self.pointsPerCanton[c]:
                    self.distances[p][p2] = 0.5
                    if p2 not in self.distances:
                        self.distances[p2] = {}
                    self.distances[p2][p] = 0.5
            self.distances[33034027][34035023] = 0
            super().__init__()
    # Now let's see how much time it takes to find a route there
    data = largeData()
    minPath, mind = data.bestRoutesFromCantonList(['C0','C49'])
    for n in range(len(minPath)):
        if n != 33 and n != 34:
            assert minPath[n] == n*1000000+(n+1)*1000
        elif n != 34:
            assert minPath[n] == 33034027
        else:
            assert minPath[n] == 34035023
    assert mind == 48*49/2 - 34

def test_initialPopulation():
    ABPop = initialPopulation(data, 5)
    assert len(ABPop) == 5
    for route in ABPop:
        d = 0
        for n in range(len(route.path)-1):
            d += data.distances[route.path[n]][route.path[n+1]]
        assert d == route.distance

def test_rankRoutes():
    pop = initialPopulation(data, 5)
    ranked = rankRoutes(pop)
    fitnesses = [fit for index,fit in ranked]
    assert sorted(fitnesses, reverse=True) == fitnesses
    for index, fit in ranked:
        assert fit == pop[index].routeFitness()

def test_selection():
    pop = initialPopulation(data, 15)
    ranked = rankRoutes(pop)
    selected = selection(ranked, 4)
    assert([i for i,f in ranked][:4] == selected[:4])

def test_breed():
    r1 = Route(data, ['A','B','C','D','E'])
    r2 = Route(data, ['C','D','A','B','E'])
    r3 = r1.breed(data, r2)
    print(r1)
    print(r2)
    print(r3)
    assert True

#def test_geneticAlgorithm():
#    bestRoute = geneticAlgorithm(data, 10, 4, 0.1, 5)
#    print (bestRoute)
#    print(bestRoute.path)
#    assert(False)
