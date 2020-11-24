import osmnx as ox
import networkx as nx
import numpy as np
import os.path

OUTPUT_PATH = './data'

def get_data(G, district_name):
    print(nx.info(G))

    # save as .osm
    path = f'{OUTPUT_PATH}/{district_name}.osm'
    if not os.path.exists(path):
        ox.save_graph_xml(G, filepath=path)

    # save as folium html
    path = f'{OUTPUT_PATH}/{district_name}_folium.html'
    if not os.path.exists(path):
        map_folium = ox.folium.plot_graph_folium(G)
        map_folium.save(path)

    # save as adjacency matrix
    path = f'{OUTPUT_PATH}/{district_name}_matrix.csv'
    if not os.path.exists(path):
        A = nx.to_numpy_matrix(G)
        np.savetxt(path, A, delimiter=",")

def plot(G, node_size=0):
    G_proj = ox.project_graph(G)
    fig, ax = ox.plot_graph(G_proj, node_size=node_size)  # ox.plot_graph(G)
    

# ox.plot_graph(ox.graph_from_place('Modena, Italy'))

# ex_1 : SAN FRANCISCO

# district_name = 'San_Francisco'

# # get NetworkX Graph
# ox.config(all_oneway=True)
# G = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')

# # print graph infomation
# print(nx.info(G))

# # plot graph
# G_proj = ox.project_graph(G)
# fig, ax = ox.plot_graph(G_proj)  # ox.plot_graph(G)

# # save as .osm
# path = f'{OUTPUT_PATH}/{district_name}.osm'
# if not os.path.exists(path):
#     ox.save_graph_xml(G, filepath=path)

# # save as folium html
# path = f'{OUTPUT_PATH}/{district_name}_folium.html'
# if not os.path.exists(path):
#     map_folium = ox.folium.plot_graph_folium(G)
#     map_folium.save(path)

# # save as adjacency matrix
# path = f'{OUTPUT_PATH}/{district_name}_matrix.csv'
# if not os.path.exists(path):
#     A = nx.to_numpy_matrix(G)
#     np.savetxt(path, A, delimiter=",")


# # ex_1 : SAN FRANCISCO

# district_name = 'San_Francisco'

# # get NetworkX Graph
# ox.config(all_oneway=True)
# wurster_hall = (37.870605, -122.254830)
# one_mile = 1609 #meters
# G = ox.graph_from_point(wurster_hall, dist=one_mile, network_type='drive')
# fig, ax = ox.plot_graph(G, node_size=0)

# # print graph infomation
# print(nx.info(G))

# # plot graph
# G_proj = ox.project_graph(G)
# ox.plot_graph(G_proj)  # ox.plot_graph(G)

# # save as .osm
# ox.save_graph_xml(G, filepath=f'{OUTPUT_PATH}/{district_name}.osm')

# # save as folium html
# map_folium = ox.folium.plot_graph_folium(G)
# map_folium.save(f'{OUTPUT_PATH}/{district_name}_folium.html')

# # save as adjacency matrix
