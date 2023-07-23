import requests
import networkx as nx
from algorithms import haversine
import pickle
import datetime


def is_erp_time(start_time, end_time, check_time):
    # Convert the time strings to datetime objects
    start_datetime = datetime.datetime.strptime(start_time, '%H:%M')
    end_datetime = datetime.datetime.strptime(end_time, '%H:%M')
    check_datetime = datetime.datetime.strptime(check_time, '%H:%M')
    
    # Check if the check_time is between start_time and end_time
    if start_datetime <= check_datetime <= end_datetime:
        return True
    else:
        return False    

def createGraph():
    # Approximate coordinates for Singapore's bounding box
    south = 1.15
    west = 103.55
    north = 1.47
    east = 104.05

    #Using overpass to get all relevant ways(Road data)
    #Data will return 2 types of element WAYS(ROAD) and NODES
    #WAYS ARE MADE FROM MULTIPLE NODES
    #https://overpass-turbo.eu/s/1xco      Example of query
    overpass_query = """
    [out:json];
    (
    way[highway][highway != "footway"][highway!="steps"][access!="private"]({south},{west},{north},{east});  // Filter by highway tag within the bounding box
    );
    out body;
    >;
    out skel qt;
    """.format(south=south, west=west, north=north, east=east)
    response = requests.get("https://overpass-api.de/api/interpreter", params={"data": overpass_query})
    data = response.json()

    #BUILDING graph
    graph = nx.DiGraph()
    #distanceGraph = nx.DiGraph()
    #Get the node from the data and place onto a graph
    for element in data["elements"]:
        if element["type"] == "node":
            node_id = element["id"]
            lon = element["lon"]
            lat = element["lat"]
            graph.add_node(node_id, pos=(lat,lon))

    #Check each ways and connect the nodes
    for element in data["elements"]:
        if element["type"] == "way":
            node_ids = element["nodes"]
            #Get speed for edge
            if "maxspeed" in element["tags"]:
                maxspeed = int(element["tags"]["maxspeed"])
            else:
                maxspeed = 50
            oneway = element["tags"].get("oneway")
            for i in range(len(node_ids) - 1):
                node1 = node_ids[i]
                node2 = node_ids[i + 1]
                lat1, lon1 = graph.nodes[node1]['pos']
                lat2, lon2 = graph.nodes[node2]['pos']
                #Get distance, time and optimal for edge
                distance = haversine(lon1, lat1, lon2, lat2)
                #Calculate time before adding addtional distance(ERP)
                time = (distance / maxspeed) * 60
                #Add ERP cost
                if node1 == 1196689060 and node2 == 5918708421:
                    current_time = datetime.datetime.now().strftime('%H:%M')
                    start_time = '07:30'
                    end_time = '09:00'
                    if is_erp_time(start_time, end_time, current_time):
                        additionalDistance = 2
                    distance = distance + additionalDistance
                
                #Get optimal value
                optimal = 0.5 * distance + 0.5 * time 

                if oneway == "yes":
                    graph.add_edge(node1, node2, distance=distance, time=time, optimal=optimal)
                else:
                    graph.add_edge(node1, node2, distance=distance, time=time, optimal=optimal)
                    graph.add_edge(node2, node1, distance=distance, time=time, optimal=optimal)


    #Save graph to file using pickle
    with open('roadmap.pkl', 'wb') as f:
        pickle.dump(graph, f)