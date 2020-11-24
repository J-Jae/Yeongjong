import osmnx as ox
import networkx as nx

OUTPUT_PATH = './data'


# ox.plot_graph(ox.graph_from_place('Modena, Italy'))

# ex_1 : SAN FRANCISCO

district_name = 'San_Francisco'

# get NetworkX Graph
ox.config(all_oneway=True)
g = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')

# print graph infomation
print(nx.info(g))

# plot graph
g_projected = ox.project_graph(g)
ox.plot_graph(g_projected)  # ox.plot_graph(g)

# save as .osm
ox.save_graph_xml(g, filepath=f'{OUTPUT_PATH}/{district_name}.osm')

# save as folium html
map_folium = ox.folium.plot_graph_folium(g)
map_folium.save(f'{OUTPUT_PATH}/{district_name}_folium.html')

# save as adjacency matrix
