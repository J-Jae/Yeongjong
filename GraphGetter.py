import osmnx as ox
import networkx as nx
import osmnxUtils
import numpy as np

# get some bbox
bbox = ox.utils_geo.bbox_from_point((45.518698, -122.679964), dist=300)
# bbox = ox.utils_geo.bbox_from_point((45.518698, -122.679964), dist=120) #test
north, south, east, west = bbox
G = ox.graph_from_bbox(north, south, east, west, network_type='drive', clean_periphery=False)

# the node degree distribution for this graph has many false cul-de-sacs
k = dict(G.degree())
{n:list(k.values()).count(n) for n in range(max(k.values()) + 1)}
G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
fig, ax = ox.plot_graph(G, node_color='r')

district_name = 'simple'
osmnxUtils.get_data(G, district_name)
osmnxUtils.get_data_drone(G, district_name)



"""
# ex_1 : SAN FRANCISCO
district_name = 'San_Francisco'
ox.config(all_oneway=True)
G = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')

# osmnxUtils.get_data(G, district_name)
G_proj = ox.project_graph(G)
fig, ax = ox.plot_graph(G_proj) 

# ex_2 : wurster_hall
district_name = 'Wurster_Hall'
wurster_hall = (37.870605, -122.254830)
one_mile = 1609 #meters  alt : 500 meters
G = ox.graph_from_point(wurster_hall, dist=one_mile, network_type='drive')

# osmnxUtils.get_data(G, district_name)
fig, ax = ox.plot_graph(G, node_size=0)


# ex_3 : get NY subway rail network
district_name = 'NY subway rail'
G = ox.graph_from_place('New York City, New York',
                        retain_all=False, truncate_by_edge=True, simplify=True,
                        custom_filter='["railway"~"subway"]')

# osmnxUtils.get_data(G, district_name)
fig, ax = ox.plot_graph(G, node_size=0, edge_color='w', edge_linewidth=0.2)

"""



'''
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

district_name += '_drone'
osmnxUtils.get_data_drone(G, district_name)
# fig, ax = ox.plot_graph(G, node_color='r')
'''