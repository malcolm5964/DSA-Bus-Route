from flask import Blueprint, render_template, jsonify, request
from algorithms import find_shortest_path_permutation, find_shortest_path_neighbour, find_shortest_path_biDirectional, haversine
from graph import createGraph
import requests
import networkx as nx
import pickle


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

    #Create graph
    #createGraph()

    with open('roadmap.pkl', 'rb') as f:
        graph = pickle.load(f)
    

    #Find shortest path using nearest neighbour with BiDirectional search
    #optimal_route_coordinates = find_shortest_path_biDirectional(graph, hotel_coordinates, "optimal")
    #distance_route_coordinates = find_shortest_path_biDirectional(graph, hotel_coordinates, "distance")

    # Find shortest path using nearest neighbour with Dijkstra's algorithm or A*
    #optimal_route_coordinates = find_shortest_path_neighbour(graph, hotel_coordinates, "optimal")
    #distance_route_coordinates = find_shortest_path_neighbour(graph, hotel_coordinates, "distance")


    #Find shortest path with Brute Force and Dijkstra
    optimal_route_coordinates = find_shortest_path_permutation(graph, hotel_coordinates, "optimal")
    distance_route_coordinates = find_shortest_path_permutation(graph, hotel_coordinates, "distance")

    return render_template('map.html', optimalLatLngs=optimal_route_coordinates, distanceLatLngs=distance_route_coordinates)  #Print on map


