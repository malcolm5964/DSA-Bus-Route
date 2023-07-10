import itertools
from itertools import permutations
import math
import networkx as nx

#Calculate distance between 2 coordinate
def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius = 6371  # Radius of the Earth in kilometers
    distance = radius * c
    return distance

# Reverse geocoding to find the nearest nodes in the graph
# As hotel coordinate are not a node on the graph, find nearest
def find_nearest_node(lat, lon, graph):
    min_distance = float('inf')
    nearest_node = None
    for node, data in graph.nodes(data=True):
        node_lat, node_lon = data['pos']
        distance = haversine(lon, lat, node_lon, node_lat)
        if distance < min_distance:
            min_distance = distance
            nearest_node = node
    return nearest_node

# ALGO 1 Create all permutation and find the shortest route
#Finding shortest route use djikstra algo
def find_shortest_path(graph, hotel_coordinates):
    num_hotels = len(hotel_coordinates)
    path_coordinates = []
    shortest_distance = float('inf')
    # Generate permutations of hotel visit order
    permutations = itertools.permutations(range(num_hotels))
    for permutation in permutations:
        sub_path_coordinates = []
        total_distance = 0.0
        for i in range(num_hotels - 1):
            hotel1 = hotel_coordinates[permutation[i]]
            hotel2 = hotel_coordinates[permutation[i + 1]]
            hotel1_node = find_nearest_node(hotel1[0], hotel1[1], graph)
            hotel2_node = find_nearest_node(hotel2[0], hotel2[1], graph)
            # Find the shortest path between two hotels
            if nx.has_path(graph, hotel1_node, hotel2_node):
                sub_path = nx.shortest_path(graph, hotel1_node, hotel2_node, weight='weight') #Return the nodes from the shortest path
                total_distance += nx.shortest_path_length(graph, hotel1_node, hotel2_node, weight='weight') #shortest_path_length() function is djikstra algo
                hotelInfo =[[hotel_coordinates[permutation[i]][2],  hotel_coordinates[permutation[i+1]][2]]] #Create an array of hotel information [hotel1 name, hotel2 name]
                sub_path_coordinates.append(hotelInfo + [[graph.nodes[node]['pos'][0], graph.nodes[node]['pos'][1]] for node in sub_path]) #Create an array(Route of all hotel) of array(Route between 2 hotel)
        #Set new shortest distance
        if total_distance < shortest_distance:
            shortest_distance = total_distance
            path_coordinates = sub_path_coordinates
    return path_coordinates


#ALGO 2 Nearest Neighbor Algorithm

