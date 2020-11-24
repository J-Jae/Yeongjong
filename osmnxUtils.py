import osmnx as ox
import networkx as nx
import numpy as np
import os.path

OUTPUT_PATH = './data'

def get_data(G, district_name):
    print(nx.info(G))
    print(f'File Path = {OUTPUT_PATH}')

    # save as .osm
    path = f'{OUTPUT_PATH}/{district_name}.osm'
    ox.config(all_oneway=True)
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

    # save as SVG
    path = f'{OUTPUT_PATH}/{district_name}_image.svg'
    fig, ax = ox.plot_graph(G, show=False, save=True, close=True, filepath=path)

    # save graph as a shapefile
    path = f'{OUTPUT_PATH}/{district_name}_shape'
    ox.save_graph_shapefile(G, filepath=path)