from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from model.carChat import CarChat
from __init__ import db

car_chat_api = Blueprint('car_chat_api', __name__, url_prefix='/api')
api = Api(car_chat_api)

class CarChatAPI:
    class _CRUD(Resource):
        def post(self):
            try:
                # Enhanced error handling
                data = request.get_json()
                
                # Validate input
                if not data or 'message' not in data:
                    return jsonify({
                        'error': 'Invalid input',
                        'message': 'Message is required'
                    }), 400
                
                # Limit message length
                if len(data['message']) > 255:
                    return jsonify({
                        'error': 'Message too long',
                        'max_length': 255
                    }), 400
                
                # Create chat message with default user
                chat = CarChat(data['message'], user_id=1)
                chat.create()
                
                return jsonify(chat.read()), 201
            
            except Exception as e:
                # Comprehensive error logging
                db.session.rollback()
                return jsonify({
                    'error': 'Internal server error',
                    'message': str(e)
                }), 500

        def get(self):
            try:
                # More efficient query
                chats = CarChat.query.order_by(CarChat.id.desc()).limit(50).all()
                
                # Use list comprehension
                allChats = [chat.read() for chat in chats]
                
                return jsonify({
                    'total_chats': len(allChats),
                    'chats': allChats
                }), 200
            
            except Exception as e:
                return jsonify({
                    'error': 'Unable to retrieve chats',
                    'message': str(e)
                }), 500

    api.add_resource(_CRUD, '/car_chat')