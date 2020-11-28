import osmnx as ox
import networkx as nx
import numpy as np
import os.path
import geopandas as gpd

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

    # save as SVG
    path = f'{OUTPUT_PATH}/{district_name}_image.svg'
    fig, ax = ox.plot_graph(G, show=False, save=True, close=True, filepath=path)

    # save graph as a shapefile and .csv
    path = f'{OUTPUT_PATH}/{district_name}_shape'
    ox.save_graph_shapefile(G, filepath=path)
    make_adjacency_matrix(district_name)

def make_adjacency_matrix(district_name):
    shp_node_path = f'{OUTPUT_PATH}/{district_name}_shape/nodes.shp'
    shp_edge_path = f'{OUTPUT_PATH}/{district_name}_shape/edges.shp'

    nodes = gpd.read_file(shp_node_path)
    edges = gpd.read_file(shp_edge_path)

    g = nx.Graph()
    
    for idx, row in nodes.iterrows():
        # add node to Graph G
        g.add_node(row['osmid'], Label=row['osmid'],
                latitude=row['y'], longitude=row['x'])

    for idx, row in edges.iterrows():
        g.add_edge(row['from'], row['to'], weight=row['length'])

    # make adjacency matrix
    nx_A = nx.to_numpy_matrix(g)
    np.savetxt(f'./data/{district_name}_adjacency_matrix.csv', nx_A, delimiter=",")