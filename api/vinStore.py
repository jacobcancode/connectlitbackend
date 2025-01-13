from flask import Blueprint, request, jsonify, Response, g
from flask_restful import Api, Resource
import requests
from sqlalchemy.exc import SQLAlchemyError
from __init__ import db
from model.vehicle import Vehicle
from api.jwt_authorize import token_required

# Create a Blueprint for the VIN decoding functionality
vinStore_api = Blueprint('vinStore_api', __name__, url_prefix='/api')
api = Api(vinStore_api)

# Base URL for the NHTSA VIN decoding API
NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"

class VINDecodeAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):
            # Retrieve the current user from the context (via JWT or session)
            current_user = g.current_user  # This assumes you are using g.current_user, set in your token_required decorator

            # Check if the current user is authenticated
            if not current_user:
                return jsonify({"message": "User is not authenticated"}), 401

            # Parse the VIN from the request
            data = request.get_json()
            vin = data.get('vin')

            # Validate the VIN
            if not vin:
                return Response("{'message': 'VIN is required'}", status=400, mimetype='application/json')

            if len(vin) != 17:
                return Response("{'message': 'VIN must be 17 characters long'}", status=400, mimetype='application/json')

            # Request data from the NHTSA API
            response = requests.get(f"{NHTSA_API_URL}{vin}?format=json")
            
            if response.status_code != 200:
                return Response("{'message': 'Failed to retrieve data from NHTSA API'}", status=500, mimetype='application/json')

            vin_data = response.json().get('Results', [{}])[0]

            # Extract necessary details
            make = vin_data.get('Make')
            model = vin_data.get('Model')
            year = vin_data.get('ModelYear')
            engine_type = vin_data.get('FuelTypePrimary')

            if not all([make, model, year, engine_type]):
                return Response("{'message': 'Incomplete data from NHTSA API'}", status=500, mimetype='application/json')

            # Check if the vehicle already exists in the database
            existing_vehicle = Vehicle.query.filter_by(vin=vin).first()
            if existing_vehicle:
                return jsonify({"message": "Vehicle already exists in the database", "vehicle": existing_vehicle.read()})

            # Create a new Vehicle object, associating it with the current user
            new_vehicle = Vehicle(vin=vin, make=make, model=model, year=year, engine_type=engine_type, uid=current_user.id)

            try:
                # Save the vehicle to the database
                db.session.add(new_vehicle)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                return Response(f"{{'message': 'Database error. User could already have VIN: {str(e)}'}}", status=500, mimetype='application/json')

            return jsonify(new_vehicle.read())

    api.add_resource(_CRUD, '/vinStore')
