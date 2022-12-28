# compute all border points between each pair of cantons

import pickle

# description of data
# - pointsPerCanton is a dictionnary with keys being the canton names
#   each value is a list of ids of points on the border
# - fixedPoint is a dict of fixed points to go through
#   each value is a pair with point id and name of the canton you're in
fh = open("InputData.pkl", 'rb')
pointsPerCanton, fixedPoints = pickle.load(fh)

borders = {}
def computeBorder(c1, c2):
    # find common points between c1 and c2
    s1 = set(pointsPerCanton[c1])
    s2 = set(pointsPerCanton[c2])
    s = list(s1.intersection(s2))
    if len(s) > 0 :
        # FIXME keep random 40 borders only
        #if len(s) > 40:
        #    s = s[:40]
        if c1 not in borders : borders[c1] = {}
        borders[c1][c2] = s
        if c2 not in borders : borders[c2] = {}
        borders[c2][c1] = s
        print(c1, '/', c2, len(borders[c1][c2]))

cantons = list(pointsPerCanton.keys())
for n1 in range(1, len(cantons)):
    for n2 in range(n1):
        computeBorder(cantons[n1], cantons[n2])
fh = open("Borders.pkl", 'wb')
pickle.dump(borders, fh)
