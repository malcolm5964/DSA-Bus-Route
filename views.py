from flask import Blueprint, render_template, jsonify, request
import requests
import numpy as np
import itertools
import networkx as nx
import json
import polyline

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

#Algorithm to get route
def tsp(graph, start_node):
    # Generate all possible permutations of the nodes
    nodes = list(graph.keys())
    permutations = list(itertools.permutations(nodes))

    min_distance = float('inf')  # Initialize with infinity
    optimal_path = []

    # Iterate through each permutation and calculate the total distance
    for path in permutations:
        current_distance = 0
        prev_node = start_node

        for node in path:
            current_distance += graph[prev_node][node]
            prev_node = node

        current_distance += graph[prev_node][start_node]

        # Update the minimum distance and optimal path if a shorter path is found
        if current_distance < min_distance:
            min_distance = current_distance
            optimal_path = path

    return optimal_path, min_distance

#Decode route geometry
def decode_route_geometry(encoded):
    if encoded:
        latlngs = polyline.decode(encoded, precision=6)
        latlngs = [[lat*10, lng*10] for lat, lng in latlngs]
        # Do something with latlngs
        return latlngs
    else:
        return None


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
    hotel_list = request.form.getlist('hotels')
    hotel_list.insert(0, "Changi Airport T3,1.3554054603062502,103.98712226757137")
    latlngs = ""

    distance_matrix = {} #Store distance between hotels in a dictionary
    for hotel in hotel_list:
        distance_matrix[hotel.split(",")[0]] = {}

    #Using onemap part

    #Getting access token
    url='https://developers.onemap.sg/privateapi/auth/post/getToken'
    account_details = {
        "email": "malcolm5964@gmail.com",
        "password": "@T0012069zmalcolm"
    }
    response = requests.post(url, json=account_details)
    token = response.json()['access_token']


    #Calculate distance between hotels and place into distance_matrix
    for index1, hotel1 in enumerate(hotel_list):
        for index2, hotel2 in enumerate(hotel_list):
            if hotel1 == hotel2:
                distance_matrix[hotel1.split(",")[0]][hotel2.split(",")[0]] = 0
                continue
            startLat = hotel1.split(",")[1]
            startLng = hotel1.split(",")[2]
            endLat = hotel2.split(",")[1]
            endLng = hotel2.split(",")[2]

            #Get distance between hotel
            DistanceUrl = f'https://developers.onemap.sg/privateapi/routingsvc/route?start={startLat},{startLng}&end={endLat},{endLng}&routeType=drive&token={token}'
            response = requests.get(DistanceUrl)
            data = response.json()
            
            #Place distance between hotels into matrix
            distance_matrix[hotel1.split(",")[0]][hotel2.split(",")[0]] = data['route_summary']['total_distance']

            #Testing drawing (Currently only draw from airport to first hotel)
            if index1==0 and index2==1:
                route_geometry = data['route_geometry'] #Route geometry is encoded route drawing info
                latlngs = decode_route_geometry(route_geometry) #Decode and get an array of lat and lng
                print(latlngs)

    

    #Calculate route to take "BRUTE FORCE METHOD"
    optimal_path, min_distance = tsp(distance_matrix, 'Changi Airport T3')            
    print("Optimal Path:", optimal_path)
    print("Minimum Distance:", min_distance)

    #Just to test/print
    pretty_print = jsonify(json.loads(json.dumps(distance_matrix, indent=4)))
    
    return render_template('map.html', latlngs=latlngs) #Print on map
