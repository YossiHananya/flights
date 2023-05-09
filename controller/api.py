import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from model.flights import Flights as flights_model

model = None

def init_app():
    global model
    model = flights_model()
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Flights, '/flights')
    
    return app


class Flights(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('flightID', required=True, location='args')
        args = parser.parse_args()
        data = model.get_flight_info(flight_id=args['flightID'])
        
        return data, 200

    def post(self):
        body_response = json.loads(request.data.decode())
        model.add_new_flights(flights=body_response['flights'])
        
        return {}, 200
