from flask import Blueprint, render_template, jsonify, request
from TSP_function import tsp_dp
from shapely.geometry import Point, LineString
import requests
import numpy as np
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
    #Get list of hotel to visit
    hotel_list = request.form.getlist('hotels')
    #Insert Changi airport at start of list
    hotel_list.insert(0, "Changi Airport T3,1.3554054603062502,103.98712226757137")

    distance_matrix = [] #Store distance between hotels in a array

    #USING ONEMAP API PART

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
        distance_matrix.append([]) #Append an array of distance between hotel1 to all other hotel to the distance_matrix
        for index2, hotel2 in enumerate(hotel_list):
            if hotel1 == hotel2:
                distance_matrix[index1].append(0)
                continue
            startLat = hotel1.split(",")[1]
            startLng = hotel1.split(",")[2]
            endLat = hotel2.split(",")[1]
            endLng = hotel2.split(",")[2]

            #Get distance between hotel
            DistanceUrl = f'https://developers.onemap.sg/privateapi/routingsvc/route?start={startLat},{startLng}&end={endLat},{endLng}&routeType=drive&token={token}'
            response = requests.get(DistanceUrl)
            data = response.json()
            
            #Place distance between hotels into array matrix
            distance_matrix[index1].append(data['route_summary']['total_distance'])


    #Calculate route to take BACK TRACKING + DYNAMIC PROGRAMMING
    min_distance, optimal_path = tsp_dp(distance_matrix, 0)            
    print("Optimal Path:", optimal_path) #[0, 3, 1, 2, 0] example of optimal path
    print("Minimum Distance:", min_distance)


    #Get incident coordinate
    incident_url = f"http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"
    headers = {
        "Accept": "application/json",
        "AccountKey": "BGf/iejfQ5+fOqFxkbLPuA=="
    }
    response = requests.get(incident_url, headers=headers)
    incident_data = response.json()
    incident_data = incident_data['value']


    #Get route geometry for optimal path and place them into latlngs array
    latlngs = []

    #Use optimal_path to get more details on the route.
    for i in range(len(optimal_path) -1):
        hotel1 = hotel_list[optimal_path[i]]
        hotel2 = hotel_list[optimal_path[i+1]]

        startName = hotel1.split(",")[0]
        endName = hotel2.split(",")[0]
        startLat = hotel1.split(",")[1]
        startLng = hotel1.split(",")[2]
        endLat = hotel2.split(",")[1]
        endLng = hotel2.split(",")[2]

        #User api to get route info again
        DistanceUrl = f'https://developers.onemap.sg/privateapi/routingsvc/route?start={startLat},{startLng}&end={endLat},{endLng}&routeType=drive&token={token}'
        response = requests.get(DistanceUrl)
        data = response.json()
        #Get the route geometry and decode(use to draw on map)
        route_geometry = data['route_geometry']
        latlng = decode_route_geometry(route_geometry)


        #logic to check for traffic incident on latlng
        route_line = LineString(latlng)

        for incident in incident_data:
            incident_lat = incident["Latitude"]
            incident_lng = incident["Longitude"]
            incident_message = incident["Message"]
            incident_point = Point(incident_lat, incident_lng)
            #Check if accident is on latlng
            if route_line.distance(incident_point) < 0.001:
                print(f"Incident at {startName} to {endName} Info: {incident_message}.")

        #Get relevant route information such as startName, endName, time, and route_instruction and place into informationArray
        #Place informationArray into latlng array to display at the sidebar later
        route_instructions = data['route_instructions']
        time = data['route_summary']['total_time']
        informationArray = [startName, endName, time, route_instructions]
        latlng.insert(0, informationArray)
        print(latlng)
        
        latlngs.append(latlng)

    return render_template('map.html', latlngs=latlngs) #Print on map