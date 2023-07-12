from flask import Blueprint, render_template, jsonify, request
from algorithms import find_shortest_path, haversine
import requests
import networkx as nx


views = Blueprint(__name__, "views")

api_key = 'AIzaSyD9pDE3krtYwqJhuCK4sEEeYSJVm5Q7JZU'
latitude = 1.3121936729272838
longitude = 103.8974076153921


def get_nearby_hotels(latitude, longitude):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{latitude},{longitude}',
        'radius': 500,
        'type': 'lodging',
        'key': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        hotels = data.get('results', [])
        if hotels:
            # latitudes = [hotel.get('geometry', {}).get('location', {}).get('lat') for hotel in hotels]
            # names = [hotel.get('name') for hotel in hotels]
            # return names
            place_ids = [hotel.get('place_id') for hotel in hotels]
            names = [hotel.get('name') for hotel in hotels]
            lats = [hotel.get("geometry").get("location").get("lat") for hotel in hotels]
            lngs = [hotel.get("geometry").get("location").get("lng") for hotel in hotels]
            hotels_dict = []
            for i in range(len(place_ids)):
                hotels_dict.append({"place_id": place_ids[i], "name": names[i], "lat": lats[i], "lng": lngs[i]})
            return hotels_dict
        else:
            print('No nearby hotels found.')
    else:
        print('Error occurred while retrieving nearby hotels.')
        print('Response:', response.text)


@views.route("/")  # this is to go to different types of pages url
def home():
    test = get_nearby_hotels(latitude, longitude)
    return render_template("index.html", hotel_names=test,
                           number_of_hotels=len(test))  # will render the html templete to the route


@views.route('/data')
def get_data():
    hotel_names = get_nearby_hotels(latitude, longitude)
    return jsonify(hotel_names=hotel_names)




@views.route('/process_form', methods=['POST'])
def process_form():
    #Get list of hotel to visit
    hotel_list = request.form.getlist('hotels')
    #Insert Changi airport at start of list
    hotel_list.insert(0, "Changi Airport T3,1.354247, 103.987324")

    #Add hotel coordinates into array
    hotel_coordinates = []
    for hotel in hotel_list:
        hotel_coordinates.append([hotel.split(",")[1], hotel.split(",")[2], hotel.split(",")[0]])

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
                time = (distance / maxspeed) * 60
                optimal = 0.5 * distance + 0.5 * time 


                if oneway == "yes":
                    graph.add_edge(node1, node2, distance=distance, time=time, optimal=optimal)

                else:
                    graph.add_edge(node1, node2, distance=distance, time=time, optimal=optimal)
                    graph.add_edge(node2, node1, distance=distance, time=time, optimal=optimal)

    # Find the shortest path using Dijkstra's algorithm
    optimal_route_coordinates = find_shortest_path(graph, hotel_coordinates)
    #distance_shortest_path = find_shortest_path(distanceGraph, hotel_coordinates)

    return render_template('map.html', optimalLatLngs=optimal_route_coordinates)  #Print on map


