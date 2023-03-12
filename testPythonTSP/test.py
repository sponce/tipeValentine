import tsplib95

# extract problem with tsplib
problemfile = 'ch130.tsp'
problem = tsplib95.load(problemfile)
nodes = list(problem.get_nodes())

# plot nodes with matplotlib and networkx
import matplotlib.pyplot as plt
import networkx as nx

G = problem.get_graph()
nx.draw_networkx_nodes(G, problem.node_coords, node_size=20);

# compute best route
tsp = nx.approximation.traveling_salesman_problem
route = tsp(G, cycle=False)
print(route)

# create closed route in nx format
pairRoute = list(nx.utils.pairwise(route))

# display route
nx.draw_networkx_edges(G, problem.node_coords, pairRoute, node_size=0, width=3)
plt.show()
