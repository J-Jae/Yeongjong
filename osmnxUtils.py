import osmnx as ox
import networkx as nx
import numpy as np
import os.path
import geopandas as gpd
import csv

PATH = './data'

def get_data(G, district_name):
    # print(nx.info(G))
    print(f'File Path = {PATH}')

    # save as graphml
    path = f'{PATH}/{district_name}.xml'
    ox.save_graphml(G, path)

    # save as .osm
    path = f'{PATH}/{district_name}.osm'
    ox.config(all_oneway=True)
    if not os.path.exists(path):
        ox.save_graph_xml(G, filepath=path)

    # save as folium html
    path = f'{PATH}/{district_name}_folium.html'
    if not os.path.exists(path):
        map_folium = ox.folium.plot_graph_folium(G)
        map_folium.save(path)

    # save as SVG
    path = f'{PATH}/{district_name}_image.svg'
    fig, ax = ox.plot_graph(G, show=False, save=True, close=True, filepath=path)

    # save graph as a shapefile and .csv
    path = f'{PATH}/{district_name}_shape'
    ox.save_graph_shapefile(G, filepath=path)

    make_adjacency_matrix(district_name)
    clean_csv(district_name)
    make_adjacency_required_matrix(district_name)

def get_data_drone(G, district_name):
    # Graph for Drones 
    district_name += '_drone'
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
                
    # save as graphml
    path = f'{PATH}/{district_name}.xml'
    ox.save_graphml(G, path)

    # save as .osm
    path = f'{PATH}/{district_name}.osm'
    ox.config(all_oneway=True)
    if not os.path.exists(path):
        ox.save_graph_xml(G, filepath=path)

    # save as folium html
    path = f'{PATH}/{district_name}_folium.html'
    if not os.path.exists(path):
        map_folium = ox.folium.plot_graph_folium(G)
        map_folium.save(path)

    # save as SVG
    path = f'{PATH}/{district_name}_image.svg'
    fig, ax = ox.plot_graph(G, show=False, save=True, close=True, filepath=path)

def make_adjacency_matrix(district_name):
    shp_node_path = f'{PATH}/{district_name}_shape/nodes.shp'
    shp_edge_path = f'{PATH}/{district_name}_shape/edges.shp'

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
    np.savetxt(f'{PATH}/{district_name}_matrix.csv', nx_A, delimiter=",")

    # drone matrix
    g = nx.Graph()
    R = 6371e3

    for idx, row in nodes.iterrows():
        g.add_node(row['osmid'], Label=row['osmid'],
                latitude=row['y'], longitude=row['x'])

    for idx, row in edges.iterrows():
        g.add_edge(row['from'], row['to'], weight=row['length'])

    for idx, from_node in nodes.iterrows():
        for idx2, to_node in nodes.iterrows():
            if(g.has_edge(from_node['osmid'], to_node['osmid'])):
                continue
            elif idx == idx2:
                continue
            else:
                lon1 = float(from_node['x'] * np.pi/180)
                lat1 = float(from_node['y'] * np.pi/180)
                lon2 = float(to_node['x'] * np.pi/180)
                lat2 = float(to_node['y'] * np.pi/180)
                d_lat = lat2 - lat1
                d_lon = lon2 - lon1
                a = np.sin(d_lat/2) ** 2 + np.cos(lat1) * \
                    np.cos(lat2) * np.sin(d_lon/2) ** 2
                c = 2 * np.arctan2(a**0.5, (1-a) ** 0.5)
                d = R * c
                d = round(d,3)
                g.add_edge(from_node['osmid'], to_node['osmid'], weight=d)

    # make adjacency matrix
    nx_A = nx.to_numpy_matrix(g)
    np.savetxt(f'{PATH}/{district_name}_drone_matrix.csv', nx_A, delimiter=",")



def clean_csv(district_name):
    read_list = []
    with open(f'{PATH}/{district_name}_matrix.csv', 'r') as file:
        for rows in file:
            row = rows.split(',')
            for i in range(len(row)):
                row[i] = round(float(row[i]), 3)
                if(row[i] == 0.0):
                    row[i] = 0
            read_list.append(row)

    with open(f'{PATH}/{district_name}_matrix.csv', 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerows(read_list)
        file.close()

        read_list = []
    with open(f'{PATH}/{district_name}_drone_matrix.csv', 'r') as file:
        for rows in file:
            row = rows.split(',')
            for i in range(len(row)):
                row[i] = round(float(row[i]), 3)
                if(row[i] == 0.0):
                    row[i] = 0
            read_list.append(row)

    with open(f'{PATH}/{district_name}_drone_matrix.csv', 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerows(read_list)
        file.close()

def make_adjacency_required_matrix(district_name):
    read_list = []
    with open(f'{PATH}/{district_name}_matrix.csv', 'r') as file:
        for rows in file:
            row = rows.split(',')
            for i in range(len(row)):
                if(float(row[i]) > 0):
                    row[i] = 1
                else:
                    row[i] = 0
            read_list.append(row)

    with open(f'{PATH}/{district_name}_matrix_required.csv', 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerows(read_list)
        file.close()

    with open(f'{PATH}/{district_name}_drone_matrix_required.csv', 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerows(read_list)
        file.close()
        
    # nx_A = nx.to_numpy_matrix(g)
    # np.savetxt(f'./data/{district_name}_matrix.csv', nx_A, delimiter=",")