import geopandas as gpd
import networkx as nx
import numpy as np

district_name = 'simple'

shp_node_path = f'./data/{district_name}_shape/nodes.shp'
shp_edge_path = f'./data/{district_name}_shape/edges.shp'

nodes = gpd.read_file(shp_node_path)
edges = gpd.read_file(shp_edge_path)
# edges = gpd.read_file(shp_edge_path, encoding='euc-kr')
# edges = gpd.read_file(shp_edge_path, encoding='euc-kr')

# shp_node = shp_node[shp_node['NODE_ID'].str[0:3] == '161']
# shp_link = shp_link[shp_link['LINK_ID'].str[0:3] == '161']

# Change column name to draw network in Gephi
# shp_node.rename(columns={'NODE_ID': 'Id'}, inplace=True)
# shp_link.rename(columns={'F_NODE': 'Source', 'T_NODE': 'Target'}, inplace=True)


print(nodes.head())
print(edges.head())

g = nx.Graph()

for idx, row in nodes.iterrows():
    # add node to Graph G
    g.add_node(row['osmid'], Label=row['osmid'],
               latitude=row['y'], longitude=row['x'])

for idx, row in edges.iterrows():
    g.add_edge(row['from'], row['to'], weight=row['length'])

# make adjacency matrix
nx_A = nx.to_numpy_matrix(g)
np.savetxt(f'./data/{district_name}_shape/adjacency_matrix.csv', nx_A, delimiter=",")

