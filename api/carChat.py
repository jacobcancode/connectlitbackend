import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from flask import Blueprint
from flask_restful import Resource, reqparse, Api
from model.carChat import CarChat
from app import db
from api.jwt_authorize import token_required
from model.carComments import CarComments
import base64
import json


# Create a single Blueprint
car_chat_bp = Blueprint('car_chat', __name__)
api = Api(car_chat_bp)

class CarChatResource(Resource):  # Renamed to avoid confusion with model
    def get(self):
        messages = CarChat.query.all()
        return [msg.read() for msg in messages], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('message', required=True, help="Message cannot be blank")
        parser.add_argument('user_id', type=int, required=True, help="User ID cannot be blank")
        args = parser.parse_args()

        new_message = CarChat(
            message=args['message'],
            user_id=args['user_id']
        )
        try:
            new_message.create()
            return new_message.read(), 201
        except Exception as e:
            return {'error': str(e)}, 400
    
        
    @token_required()  # Ensure the user is authenticated
    def delete(self):
        # Obtain the current user
        current_user = g.current_user
        # Obtain the request data
        data = request.get_json()
        
        # Find the current message from the database table(s)
        message = CarChat.query.get(data['id'])
        
        if message is None:
            return jsonify({"error": "Message not found"}), 404
        
        # Check if the current user is the owner of the message
        if message._user_id != current_user.id:
            return jsonify({"message": "You are not authorized to delete this message"}), 403
        
        # Delete the message using the ORM method defined in the model
        message.delete()
        
        # Return response
        return jsonify({"message": "Message deleted successfully"}), 200

    @token_required()  # Ensure the user is authenticated
    def put(self):
        # Obtain the current user
        current_user = g.current_user
        # Obtain the request data
        data = request.get_json()
        
        # Find the current message from the database table(s)
        message = CarChat.query.get(data['id'])
        
        if message is None:
            return jsonify({"error": "Message not found"}), 404
        
        # Check if the current user is the owner of the message
        if message._user_id != current_user.id:
            return jsonify({"message": "You are not authorized to edit this message"}), 403
        
        # Update the message content
        message._message = data['message']  # Update with new message content
        message.update()  # Call the update method to save changes
        
        # Return response with updated message data
        return jsonify(message.read()), 200

# Register the resource
api.add_resource(CarChatResource, '/car_chat')

