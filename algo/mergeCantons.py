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
   "Kanton Bern",
   "Canton de Fribourg",
   "Canton de Genève",
   "Kanton Glarus",
   "Kanton Graubünden",
   "Kanton Luzern",
   "Canton de Neuchâtel",
   "Kanton Nidwalden",
   "Kanton Obwalden",
   "Kanton Schaffhausen",
   "Kanton Schwyz",
   "Kanton Solothurn",
   "Kanton St. Gallen",
   "Kanton Thurgau",
   "Kanton Uri",
   "Canton de Vaud",
   "Kanton Zug",
   "Kanton Zürich",
   "Canton Ticino",
   "Canton du Jura",
   "Kanton Wallis",
]

cantonBorders = {}
for name in cantonNames:
    cantonBorders[name] = {tuple(sorted(k[:2])) : 1 for k in getCanton(name)}

allExits = {}
n = 0
for name in cantonBorders:
    print ("%s has %d exits" % (name, len(cantonBorders[name])))
    new = cantonBorders[name]
    allExits = {k:allExits.get(k,0)+new.get(k,0) for k in set(allExits)|set(new)}
    n += len(new)

print ("In total %d exits, so %d are duplicates" % (len(allExits), n - len(allExits)))
dup = [k for k,v in allExits.items() if v > 1]
print (len(dup))

points = { k : list(set(cantonBorders[k]) & set(dup)) for k in cantonNames }
for name in cantonBorders:
    print ("%s has %d real exits" % (name, len(points[name])))

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

