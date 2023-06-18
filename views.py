from flask import Blueprint, render_template, jsonify, request
import requests
import numpy as np

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
    hotel_list = request.form.getlist('hotels')

    number_of_hotel = len(hotel_list)
    distance_matrix = np.empty((number_of_hotel, number_of_hotel))  #Store distance between hotels

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
                distance_matrix[index1][index2] = 0
            startLat = hotel1.split(",")[1]
            startLng = hotel1.split(",")[2]
            endLat = hotel2.split(",")[1]
            endLng = hotel2.split(",")[2]

            DistanceUrl = f'https://developers.onemap.sg/privateapi/routingsvc/route?start={startLat},{startLng}&end={endLat},{endLng}&routeType=drive&token={token}'
            response = requests.get(DistanceUrl)
            data = response.json()

            distance_matrix[index1][index2] = data['route_summary']['total_distance']
            
    #Just for checking
    for row in distance_matrix:
        for element in row:
            print(element, end="\t")
        print()

    return distance_matrix.tolist()
