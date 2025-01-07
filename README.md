# INF1008 Python Project (DSA)
<b>TransitPro</b>

<img src="https://github.com/DeNhAiKal/INF1008/blob/main/static/MainLogo.png" data-canonical-src="https://github.com/DeNhAiKal/INF1008/blob/main/static/MainLogo.png" width="200" height="200" />

## Getting Started
### Manual Installation
1. Using pip install, install them in the following way:
    -     pip install flask
    -     pip install networkx
    -     pip install pickle
    -     pip install itertools
2. You should be all set!

## Running Application
1.  Run the python file "app.py"
    -     python app.py
3.  Take note of the IP address shown in the console. Append "/index" to access the site.
    -     http://127.0.0.1:8000/index

## Developed With

* [Python 3.7](https://docs.python.org/3.7/) - Language used
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [Overpass API](https://www.geofabrik.de/data/overpass-api.html) - Provides access to OpenStreetMap(OSM) data
* ![image](https://github.com/user-attachments/assets/5f899633-3484-42a8-8e4b-f6f430855576)![image](https://github.com/user-attachments/assets/10e0ae79-23a8-4cb9-9d12-4a59df4b8295)


* [Google Map API](https://developers.google.com/maps/documentation) - Used to create a map displaying the routes for the hotels picked by the user.
* [NetworkX](https://networkx.org/documentation/stable/reference/introduction.html) - Used to create graphs to calculate the routes (1. Add 'node' to graph 2. Add edge to graph base on 'way' data)

---

## Website Features

### **Hotel Selection Page**

The Hotel Selection Page allows users to select nearby hotels based on their location. It leverages Google Maps to display markers for each hotel and calculates the optimal routes between selected locations. Below is a preview:

![Hotel Selection Page](https://github.com/user-attachments/assets/77d22202-d4c2-472e-b398-06936989ffc1)

### **Optimal Route Page**

The Optimal Route Page displays the route designed to minimize costs and maximize efficiency. This feature is tailored for time-critical operations and cost-effective travel. Below is a preview:

![Optimal Route Page](https://github.com/user-attachments/assets/023b588e-e950-4a64-bb23-459a44b1d4a9)
* Time Efficiency: The optimal route minimizes travel time by considering traffic patterns, road conditions, and other factors. It ensures the journey is completed as quickly as possible, making it ideal for time-sensitive tasks.
* Cost-Effectiveness: By factoring in fuel consumption, toll fees, and other expenses, the optimal route reduces overall travel costs, making it an economically sound choice.
* Maximizing Resource Utilization: The route optimizes vehicle capacity and load distribution, ensuring efficient resource management and reducing operational costs.

### **Distance Route Page**

The Distance Route Page focuses on minimizing the distance traveled. This feature is especially useful when resources are constrained or when time is of the essence. Below is a preview:

![Distance Route Page](https://github.com/user-attachments/assets/b6cd2152-3399-43fb-bbc0-612ea8845b83)
* Resource Constraints: In scenarios with limited fuel, time, or budget, prioritizing distance helps minimize resource usage, making it practical for cost-effective operations.
* Time Sensitivity: When time is critical, selecting the shortest distance route ensures quick delivery or response, which is crucial for emergency situations, logistics, and other time-sensitive services.
* Traffic or Road Conditions: While the optimal route may involve complex traffic or toll roads, a shorter distance can bypass such complexities, potentially resulting in a quicker overall travel time.

---



