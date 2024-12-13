from flask import Blueprint
from flask_restful import Resource, reqparse
from app import db  # Import the db instance

# Define the ChatMessage model directly in this file
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<ChatMessage {self.message}>'

# Create a Blueprint
car_chat_bp = Blueprint('car_chat', __name__)

class CarChat(Resource):
    def get(self):
        messages = ChatMessage.query.all()
        return [{'id': msg.id, 'message': msg.message} for msg in messages], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('message', required=True, help="Message cannot be blank")
        args = parser.parse_args()

        new_message = ChatMessage(message=args['message'])
        db.session.add(new_message)
        db.session.commit()

        return {'message': f"Received: {args['message']}"}, 201

# Register the resource with the Blueprint
from flask_restful import Api

api = Api(car_chat_bp)
api.add_resource(CarChat, '/carchat')

car_chat_api = Blueprint('car_chat', __name__)

@car_chat_api.route('/car_chat', methods=['GET'])
def some_function():
    return "Hello from car chat!"

