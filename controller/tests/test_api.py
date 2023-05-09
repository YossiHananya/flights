


import json
import requests

def test_get_flight_info():
    response = requests.get('http://localhost:5000/flights', params={"flightID": "G86"})
    print(response.content)
    assert response.status_code == 200


def test_add_new_flights():
    data={"flights": [
        {'flight ID': 'Z99', 'Arrival':'20:00', 'Departure':'21:00'},
        {'flight ID': 'Invalid', 'Arrival':'20:00'},
    ]} 
    
    response = requests.post('http://localhost:5000/flights', data=json.dumps(data))
    print(response.content)
    
    assert response.status_code == 200
    