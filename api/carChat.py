from flask import Blueprint
from flask_restful import Resource, reqparse, Api
from model.carChat import CarChat
from app import db

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

# Register the resource
api.add_resource(CarChatResource, '/car_chat')

