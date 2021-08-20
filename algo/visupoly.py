import matplotlib.pyplot as plt
import json

def disp(name, color):
    data = json.load(open("../swissBoundaries/Cantons/%s"%name,'r'))
    for feat in data['features']:
        coords = feat['geometry']['coordinates']
        for pol in coords:
            x = [c[0] for c in pol]
            y = [c[1] for c in pol]
            ax.plot(x,y,color=color)

fig = plt.figure()
ax = fig.gca()
disp('swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.geojson', 'gray')
disp('Canton-Appenzell Innerrhoden-4.geojson','green')

ax.axis('scaled')
plt.show()
