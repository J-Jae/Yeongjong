
def get_shortest_paths_distances(graph, pairs, edge_weight_name):
    """Compute shortest distance between each pair of nodes in a graph.  Return a dictionary keyed on node pairs (tuples)."""
    distances = {}
    for pair in pairs:
        distances[pair] = nx.dijkstra_path_length(
            graph, pair[0], pair[1], weight=edge_weight_name)
    return distances


pairs = [('A', 'B'),
         ('A', 'E'),
         ('A', 'C'),
         ('A', 'D'),
         ('A', 'M'),
         ]

shortest_paths = get_shortest_paths_distances(g, pairs, 'distance')
# print(shortest_paths)

# dijkstra example
dijkstra_path = nx.dijkstra_path(g, source='A', target='M', weight='distance')
dijkstra_path_length = nx.dijkstra_path_length(
    g, source='A', target='M', weight='distance')
print('dijkstra_path : ', dijkstra_path)
print('dijkstra_path_length : ', dijkstra_path_length)

path = nx.single_source_dijkstra_path(g, source='A', weight='distance')
# print(path)
