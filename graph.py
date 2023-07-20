import requests
import networkx as nx
from algorithms import haversine
import pickle

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
    #Get speed bands
    traffic_flow_url = f"http://datamall2.mytransport.sg/ltaodataservice/v3/TrafficSpeedBands"
    headers = {
        "Accept": "application/json",
        "AccountKey": "BGf/iejfQ5+fOqFxkbLPuA=="
    }

    response = requests.get(traffic_flow_url, headers=headers)
    traffic_flow_data = response.json()
    traffic_flow_data = traffic_flow_data['value']

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
                #Add ERP cost
                if node1 == 1196689060 and node2 == 5918708421:
                    distance = distance + 5
                time = (distance / maxspeed) * 60
                optimal = 0.5 * distance + 0.5 * time 

                if oneway == "yes":
                    graph.add_edge(node1, node2, distance=distance, time=time, optimal=optimal)
                else:
                    graph.add_edge(node1, node2, distance=distance, time=time, optimal=optimal)
                    graph.add_edge(node2, node1, distance=distance, time=time, optimal=optimal)


    #Save graph to file using pickle
    with open('roadmap.pkl', 'wb') as f:
        pickle.dump(graph, f)