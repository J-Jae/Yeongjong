import geopandas as gpd
import networkx as nx
import numpy as np
from GenericAlgorithm import *
import osmnx as ox
import json

def save_dict_to_file(dic, district_name):
    f = open(f'./data/{district_name}_result.txt','w')
    f.write(str(dic))
    f.close()

"""
Settings
"""
district_name = 'simple_drone'
"""
Settings
"""

path = f'./data/{district_name}_matrix'
ga = GenericAlgorithm(path, generations=500, population_size=300, alpha=3)
result = ga.run()

# get Graph from graphml
g = ox.load_graphml(f'./data/{district_name}.xml')
g = nx.to_undirected(g)

# save result
save_dict_to_file(result, district_name)

# convert index to node_id
route = []
route.append(result['route'][0][0])
for edge in result['route']:
    route.append(edge[1])

# route
nodes = list(g.nodes.data())
for i in range(len(route)):
    route[i] = nodes[route[i]][0]

# plot and save result
# fig, ax = ox.plot_graph_route(g, route, orig_dest_size=0, node_size=0)
path = f'./data/{district_name}_result.svg'
fig, ax = ox.plot_graph_route(g, route, orig_dest_size=0, node_size=0, save=True, filepath=path)


'''
g = ox.load_graphml(f'./data/{district_name}_drone.xml')
g2 = nx.to_undirected(g)

fig, ax = ox.plot_graph(g2, node_color='r')
'''



