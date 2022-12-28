import pickle

def getCanton(name):
    fh = open("%s-exits.pkl" % name, 'rb')
    return pickle.load(fh)

cantonNames = [
   "Kanton Aargau",
   "Kanton Appenzell Ausserrhoden",
   "Kanton Appenzell Innerrhoden",
   "Kanton Basel-Landschaft",
   "Kanton Basel-Stadt",
   # "Kanton Bern",
   # "Canton de Fribourg",
   # "Canton de Genève",
   # "Kanton Glarus",
   # "Kanton Graubünden",
   # "Kanton Luzern",
   # "Canton de Neuchâtel",
   # "Kanton Nidwalden",
   # "Kanton Obwalden",
   # "Kanton Schaffhausen",
   # "Kanton Schwyz",
   # "Kanton Solothurn",
   # "Kanton St. Gallen",
   # "Kanton Thurgau",
   # "Kanton Uri",
   # "Canton de Vaud",
   # "Kanton Zug",
   # "Kanton Zürich",
   # "Canton Ticino",
   # "Canton du Jura",
   # "Kanton Wallis",
]

# dictionnary of ids on the borders with the number of times they
# are used, so for a given canton, always 1
cantonBorders = {}
for name in cantonNames:
    cantonBorders[name] = {id : 1 for id in getCanton(name)}

# dictionnary of ids on the borders with the number of times they
# are used, so > 1 if on an inner border as it will appear on both
# cantons on each side of the border
allExits = {}
n = 0
for name in cantonBorders:
    new = cantonBorders[name]
    n += len(new)
    print ("%s initially has %d exits" % (name, len(new)))
    allExits = {k:allExits.get(k,0)+new.get(k,0) for k in set(allExits)|set(new)}

print ("In total only %d exits, was %d before deduplication" % (len(allExits), n))
# set of points on inner borders
dup = [k for k,v in allExits.items() if v > 1]
print ("And only %d 'inner' exits" % len(dup))

# keep only points on inner borders for each canton
points = { k : list(set(cantonBorders[k]) & set(dup)) for k in cantonNames }
for name in cantonBorders:
    print ("%s has %d 'inner' exits" % (name, len(points[name])))

# drop borders that can be dropped
#toBeDropped = [
#    ( "Canton de Genève", "Canton de Vaud" ),
#    ( "Canton de Vaud", "Canton de Fribourg" ),
#    ( "Canton de Vaud", "Kanton Wallis" ),
#    ( "Canton de Fribourg", "Kanton Bern" ),
#    ( "Canton de Vaud", "Kanton Bern" ),
#    ( "Kanton Wallis", "Kanton Bern" ),
#]

#nb = sum([len(points[n]) for n in points])
#for c1, c2 in toBeDropped:
#    common = set(cantonBorders[c1]) & set(cantonBorders[c2])
#    points[c1] = [v for v in points[c1] if v not in common]
#    points[c2] = [v for v in points[c2] if v not in common]
#print ("Dropping some borders went from %d to %d points" % (nb, sum([len(points[n]) for n in points])))
#for c1, c2 in toBeDropped:
#    if c1 in points:
#        points[c2] = points[c1] + points[c2]
#        del points[c1]

additions = { "Velosophe" : (871856370, "Canton de Genève"),
              "Chocolarium" : (4466095934, "Kanton St. Gallen"),
              "Cheese shop" : (320349073, "Canton de Fribourg"),
              "Butcher shop" : (3041241876, "Kanton Wallis"),
              "Maison de la tete de moine" : (3675033536, "Kanton Bern"),
              "Salami shop" : (1479486535, "Canton Ticino"),
              "BackeryKeller" : (1286482374, "Kanton St. Gallen"),
              "BERN" : (33202504, "Kanton Bern"),
             }

fh = open("InputData.pkl", 'wb')
pickle.dump((points, additions), fh)

