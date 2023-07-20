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

#Get route information such as distance, time or optimal
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
    shortest_total_route_coordinates = []  #[[Hotel1 to Hotel2 latlng][Hotel2 to Hotel3 latlng]....]
    shortest_route = float('inf')

    # Generate permutations of hotel visit order
    permutations = itertools.permutations(range(num_hotels))
    for permutation in permutations:
        sub_path_coordinates = []
        route_distance = 0.0

        for i in range(num_hotels - 1):
            hotel1 = hotel_coordinates[permutation[i]]
            hotel2 = hotel_coordinates[permutation[i + 1]]
            hotel1_node = find_nearest_node(hotel1[0], hotel1[1], graph)
            hotel2_node = find_nearest_node(hotel2[0], hotel2[1], graph)

            # Find the shortest path between two hotels
            if nx.has_path(graph, hotel1_node, hotel2_node):

                #calculate shortest path with djikstra algo
                route_distance += nx.shortest_path_length(graph, hotel1_node, hotel2_node, weight='optimal') 
                #Return the nodes that make shortest path
                route_nodes = nx.shortest_path(graph, hotel1_node, hotel2_node, weight='optimal') 
                #Get the distance and time for route
                optimal_distance = get_route_info(graph, route_nodes, "distance") 
                optimal_time = get_route_info(graph, route_nodes, "time")

                #Create an array of hotel information [hotel1 name, hotel2 name, time, distance]
                optimalHotelInfo =[[hotel_coordinates[permutation[i]][2],  hotel_coordinates[permutation[i+1]][2], optimal_time, optimal_distance]] 
                
                #With the shortest path node, get the lat and lng to draw on map
                sub_path_coordinates.append(optimalHotelInfo + [[graph.nodes[node]['pos'][0], graph.nodes[node]['pos'][1]] for node in route_nodes]) 

        #Set new shortest distance
        if route_distance < shortest_route:
            shortest_route = route_distance
            shortest_total_route_coordinates = sub_path_coordinates

    return shortest_total_route_coordinates


#ALGO 2 Nearest Neighbor Algorithm with Djikstra and A*
def find_shortest_path_neighbour(graph, hotel_coordinates, weight):
    num_hotels = len(hotel_coordinates)
    visited = set()
    total_route_coordinates = []
    current_hotel = hotel_coordinates[0]

    #Get the  straight-line distance between 2 nodes base on coordinates in graph
    def heuristic_func(node1, node2):
        x1, y1 = graph.nodes[node1]['pos']
        x2, y2 = graph.nodes[node2]['pos']
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx*dx + dy*dy)

    while len(visited) < num_hotels-1:
        visited.add(tuple(current_hotel))
        nearest_hotel = None
        min_distance = float('inf')

        currentHotel_node = find_nearest_node(current_hotel[0], current_hotel[1], graph)


        for hotel in hotel_coordinates:
            if tuple(hotel) not in visited:
                hotel_node = find_nearest_node(hotel[0], hotel[1], graph)
                #Djikstra Algorithm
                #distance = nx.shortest_path_length(graph, currentHotel_node, hotel_node, weight=weight)

                #A* Algorithm
                distance = nx.astar_path_length(graph, currentHotel_node, hotel_node, heuristic=heuristic_func, weight=weight)

                if distance < min_distance:
                    min_distance = distance
                    nearest_hotel = hotel

        #Get node of nearest hotel
        nearestHotel_node = find_nearest_node(nearest_hotel[0], nearest_hotel[1], graph)

        #Djikstra Algorithm Get path nodes
        #optimal_sub_path = nx.shortest_path(graph, currentHotel_node, nearestHotel_node, weight=weight)

        #A* Algorithm Get path nodes
        route_node = nx.astar_path(graph, currentHotel_node, nearestHotel_node, heuristic=heuristic_func, weight=weight)

        #Get time and distance of route
        route_time = get_route_info(graph, route_node, "time")
        route_distance = get_route_info(graph, route_node, "distance")

        #Get hotel name, route time, route distance into array
        optimalHotelInfo =[[current_hotel[2],  nearest_hotel[2], route_time,route_distance]] 

        #Append [hotel information and route lat lng] into total route coordinate
        total_route_coordinates.append(optimalHotelInfo + [[graph.nodes[node]['pos'][0], graph.nodes[node]['pos'][1]] for node in route_node])

        #Change the current hotel to nearest hotel
        current_hotel = nearest_hotel 
        

    return total_route_coordinates



#ALGO 3 Nearest Neighbor Algorithm with Bidirectional search
def bidirectional_search(graph, source, target):
    forward_queue = [(source, None)]
    backward_queue = [(target, None)]
    forward_visited = {source: None}
    backward_visited = {target: None}
    common_node = None

    while forward_queue and backward_queue:
        forward_node, forward_parent = forward_queue.pop(0)
        backward_node, backward_parent = backward_queue.pop(0)
        forward_neighbors = graph.neighbors(forward_node)
        backward_neighbors = graph.predecessors(backward_node)

        for neighbor in forward_neighbors:
            if neighbor not in forward_visited:
                forward_visited[neighbor] = forward_node
                forward_queue.append((neighbor, forward_node))
            if neighbor in backward_visited:
                common_node = neighbor
                break

        for neighbor in backward_neighbors:
            if neighbor not in backward_visited:
                backward_visited[neighbor] = backward_node
                backward_queue.append((neighbor, backward_node))
            if neighbor in forward_visited:
                common_node = neighbor
                break

        if common_node:
            break

    if common_node:
        forward_path = []
        node = common_node
        while node != source:
            forward_path.append(node)
            node = forward_visited[node]
        forward_path.append(source)
        forward_path.reverse()

        backward_path = []
        node = common_node
        while node != target:
            backward_path.append(node)
            node = backward_visited[node]
        backward_path.append(target)

        final_path = forward_path + backward_path[1:]  # Combine paths, excluding common node
        return final_path

    return None

def find_shortest_path_biDirectional(graph, hotel_coordinates):
    num_hotels = len(hotel_coordinates)
    visited = set()
    total_route_coordinates = []         #Store all the subroute to form complete route
    current_hotel = hotel_coordinates[0] #Store start hotel

    while len(visited) < num_hotels-1:
        visited.add(tuple(current_hotel))
        nearest_hotel = None #Store nearest hotel from start hotel
        min_distance = float('inf') #Store lowest distance from start hotel to next hotel
        route_nodes = [] #Store the lowest distance route 

        currentHotel_node = find_nearest_node(current_hotel[0], current_hotel[1], graph)


        for hotel in hotel_coordinates:
            if tuple(hotel) not in visited:
                hotel_node = find_nearest_node(hotel[0], hotel[1], graph)

                #Bidirectional Algorithm
                route = bidirectional_search(graph, currentHotel_node, hotel_node) #Return the nodes in the route
                distance = get_route_info(graph, route, "optimal")

                if distance < min_distance:
                    route_nodes = route
                    min_distance = distance
                    nearest_hotel = hotel

        #Get time for route
        route_time = get_route_info(graph, route_nodes, "time") 
        #Get distance for route
        route_distance = get_route_info(graph, route_nodes, "distance") 
        #Get hotel name, route time, route distance into array
        optimalHotelInfo =[[current_hotel[2],  nearest_hotel[2], route_time, route_distance]]
        #Append [hotel information and route lat lng] into total route coordinate
        total_route_coordinates.append(optimalHotelInfo + [[graph.nodes[node]['pos'][0], graph.nodes[node]['pos'][1]] for node in route_nodes])
        #Change the current hotel to nearest hotel
        current_hotel = nearest_hotel 
        

    return total_route_coordinates
