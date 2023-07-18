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


def get_route_info(graph, optimal_sub_path, type):
    total_info = 0
    for i in range(len(optimal_sub_path) -1):
        currentNode = optimal_sub_path[i]
        nextNode = optimal_sub_path[i+1]
        info = graph[currentNode][nextNode][type]
        total_info += info
    return total_info




# ALGO 1 Create all permutation and find the shortest route
#Finding shortest route use djikstra algo
def find_shortest_path_permutation(graph, hotel_coordinates):
    num_hotels = len(hotel_coordinates)
    optimal_route_coordinates = []  #[[Hotel1 to Hotel2 latlng][Hotel2 to Hotel3 latlng]....]
    optimal_shortest_weight = float('inf')

    # Generate permutations of hotel visit order
    permutations = itertools.permutations(range(num_hotels))
    for permutation in permutations:
        optimal_sub_path_coordinates = []
        optimal_weight = 0.0

        for i in range(num_hotels - 1):
            hotel1 = hotel_coordinates[permutation[i]]
            hotel2 = hotel_coordinates[permutation[i + 1]]
            hotel1_node = find_nearest_node(hotel1[0], hotel1[1], graph)
            hotel2_node = find_nearest_node(hotel2[0], hotel2[1], graph)

            # Find the shortest path between two hotels
            if nx.has_path(graph, hotel1_node, hotel2_node):

                
                optimal_weight += nx.shortest_path_length(graph, hotel1_node, hotel2_node, weight='optimal') #calculate shortest path with djikstra algo
                optimal_sub_path = nx.shortest_path(graph, hotel1_node, hotel2_node, weight='optimal') #Return the nodes that make shortest path
                optimal_distance = get_route_info(graph, optimal_sub_path, "distance") #Get the distance for optimal route
                optimal_time = get_route_info(graph, optimal_sub_path, "time") #Get the time for optimal route

                #Create an array of hotel information [hotel1 name, hotel2 name, time, distance]
                optimalHotelInfo =[[hotel_coordinates[permutation[i]][2],  hotel_coordinates[permutation[i+1]][2], optimal_time, optimal_distance]] 
                
                #With the shortest path node, get the lat and lng to draw on map
                optimal_sub_path_coordinates.append(optimalHotelInfo + [[graph.nodes[node]['pos'][0], graph.nodes[node]['pos'][1]] for node in optimal_sub_path]) 

        #Set new shortest distance
        if optimal_weight < optimal_shortest_weight:
            optimal_shortest_weight = optimal_weight
            optimal_route_coordinates = optimal_sub_path_coordinates

    return optimal_route_coordinates


#ALGO 2 Nearest Neighbor Algorithm
def find_shortest_path_neighbour(graph, hotel_coordinates):
    num_hotels = len(hotel_coordinates)
    visited = set()
    optimal_route_coordinates = []
    current_hotel = hotel_coordinates[0]

    def heuristic_func(node1, node2):
        x1, y1 = graph.nodes[node1]['pos']
        x2, y2 = graph.nodes[node2]['pos']
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx*dx + dy*dy)

    while len(visited) < num_hotels-1:
        #print(len(visited))
        visited.add(tuple(current_hotel))
        nearest_hotel = None
        min_distance = float('inf')

        currentHotel_node = find_nearest_node(current_hotel[0], current_hotel[1], graph)


        for hotel in hotel_coordinates:
            if tuple(hotel) not in visited:
                hotel_node = find_nearest_node(hotel[0], hotel[1], graph)
                #Djikstra Algorithm
                #distance = nx.shortest_path_length(graph, currentHotel_node, hotel_node, weight='optimal')
                #A* Algorithm
                distance = nx.astar_path_length(graph, currentHotel_node, hotel_node, heuristic=heuristic_func, weight='optimal')
                if distance < min_distance:
                    min_distance = distance
                    nearest_hotel = hotel

        print(nearest_hotel)
        nearestHotel_node = find_nearest_node(nearest_hotel[0], nearest_hotel[1], graph)
        #Djikstra Algorithm
        #optimal_sub_path = nx.shortest_path(graph, currentHotel_node, nearestHotel_node, weight='optimal')
        #A* Algorithm
        optimal_sub_path = nx.astar_path(graph, currentHotel_node, nearestHotel_node, heuristic=heuristic_func, weight='optimal')
        optimal_time = get_route_info(graph, optimal_sub_path, "time") #Get the time for optimal route
        optimal_distance = get_route_info(graph, optimal_sub_path, "distance") #Get the time for optimal route
        optimalHotelInfo =[[current_hotel[2],  nearest_hotel[2], optimal_time, optimal_distance]] 
        optimal_route_coordinates.append(optimalHotelInfo + [[graph.nodes[node]['pos'][0], graph.nodes[node]['pos'][1]] for node in optimal_sub_path])
        #Change the current hotel to nearest hotel
        current_hotel = nearest_hotel 
        

    return optimal_route_coordinates

        