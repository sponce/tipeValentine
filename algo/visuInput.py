import pickle
import matplotlib.pyplot as plt

fh = open("InputNodes.pkl", 'rb')
points, additions, allNodes = pickle.load(fh)

fh = open("weights.pkl", 'rb')
weights = pickle.load(fh)

ax = plt.subplot()

for k in allNodes:
    node = allNodes[k]
    ax.plot(node['lon'], node['lat'], 'gx')

print(weights)
for ai in weights:
    for bi in weights[ai]:
        a = allNodes[ai]
        b = allNodes[bi]
        ax.plot([a['lon'], b['lon']], [a['lat'], b['lat']], 'b')

plt.show()
