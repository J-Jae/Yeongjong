import osmnx as ox
import networkx as nx
import numpy as np
import os.path
import geopandas as gpd
import csv
import osmnxUtils


# get some bbox
bbox = ox.utils_geo.bbox_from_point((45.518698, -122.679964), dist=300)
north, south, east, west = bbox
G = ox.graph_from_bbox(north, south, east, west, network_type='drive', clean_periphery=False)

# the node degree distribution for this graph has many false cul-de-sacs
k = dict(G.degree())
{n:list(k.values()).count(n) for n in range(max(k.values()) + 1)}
G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
# fig, ax = ox.plot_graph(G, node_color='r')

# Graph for Drones 
R = 6371e3
nodes = list(G.nodes.data())

for i in range(len(nodes)):
    for j in range(len(nodes)):
        if i==j or (G.has_edge(nodes[i][1]['osmid'], nodes[j][1]['osmid'])):
            continue
        else:
            lon1 = float(nodes[i][1]['x'] * np.pi/180)
            lat1 = float(nodes[i][1]['y'] * np.pi/180)
            lon2 = float(nodes[j][1]['x'] * np.pi/180)
            lat2 = float(nodes[j][1]['y'] * np.pi/180)
            d_lat = lat2 - lat1
            d_lon = lon2 - lon1
            a = np.sin(d_lat/2) ** 2 + np.cos(lat1) * \
                np.cos(lat2) * np.sin(d_lon/2) ** 2
            c = 2 * np.arctan2(a**0.5, (1-a) ** 0.5)
            d = R * c
            d = round(d,3)
            G.add_edge(nodes[i][1]['osmid'], nodes[j][1]['osmid'], length=d)

fig, ax = ox.plot_graph(G, node_color='r')