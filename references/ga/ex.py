import itertools
import copy
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import random

# edgelist = pd.read_csv('https://gist.githubusercontent.com/brooksandrew/e570c38bcc72a8d102422f2af836513b/raw/89c76b2563dbc0e88384719a35cba0dfc04cd522/edgelist_sleeping_giant.csv')
edgelist = pd.read_csv('C:/Projcet/ga/iiac3_edge.csv')

# nodelist = pd.read_csv('https://gist.githubusercontent.com/brooksandrew/f989e10af17fb4c85b11409fea47895b/raw/a3a8da0fa5b094f1ca9d82e1642b384889ae16e8/nodelist_sleeping_giant.csv')
nodelist = pd.read_csv('C:/Projcet/ga/iiac3_node.csv')

# init graph
g = nx.Graph()

# Add edges and edge attributes
for i, elrow in edgelist.iterrows():
    g.add_edge(elrow[0], elrow[1], trail=elrow['trail'],
               distance=elrow['distance'], color=elrow['color'], required=['required'])

for i, nlrow in nodelist.iterrows():
    g.add_node(nlrow['id'], num=nlrow['node'], x=nlrow['X'], y=nlrow['Y'])

# Genetic Algorithm


def get_shortest_paths_distances(graph, pairs, edge_weight_name):
    """Compute shortest distance between each pair of nodes in a graph.  Return a dictionary keyed on node pairs (tuples)."""
    distances = {}
    for pair in pairs:
        distances[pair] = nx.dijkstra_path_length(
            graph, pair[0], pair[1], weight=edge_weight_name)
    return distances


# pairs = [('A', 'B'),
#          ('A', 'E'),
#          ('A', 'C'),
#          ('A', 'D'),
#          ('A', 'M'),
#          ]


# shortest_paths = get_shortest_paths_distances(g, pairs, 'distance')
# print(shortest_paths)
###########
###########
###########
###########
###########

# Draw Graph
pos = {node[0]: (node[1]['x'], node[1]['y']) for node in g.nodes(data=True)}
edge_colors = [edge[2]['color'] for edge in g.edges(data=True)]

plt.figure(figsize=(8, 6))
nx.draw(g, pos=pos, edge_color=edge_colors, node_size=0,
        node_color='black', with_labels=True, font_size=15)
labels = nx.get_edge_attributes(g, 'distance')
nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)
plt.title('Incheon Airport', size=15)
plt.show()
