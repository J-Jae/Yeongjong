import osmnx as ox
import networkx as nx
import osmnxUtils
OUTPUT_PATH = './data'


# ex_1 : SAN FRANCISCO
district_name = 'San_Francisco'
ox.config(all_oneway=True)
G = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')

osmnxUtils.get_data(G, district_name)
osmnxUtils.plot(G)

# ex_2 : wurster_hall
district_name = 'Wurster_Hall'
wurster_hall = (37.870605, -122.254830)
one_mile = 1609 #meters
# one_mile = 500 #meters
G = ox.graph_from_point(wurster_hall, dist=one_mile, network_type='drive')

osmnxUtils.get_data(G, district_name)
osmnxUtils.plot(G)