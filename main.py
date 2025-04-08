# imports from flask
import json
import os
import ast
from urllib.parse import urljoin, urlparse
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from flask.cli import AppGroup
from werkzeug.security import generate_password_hash
import shutil
import datetime
import jwt
from functools import wraps
from datetime import timedelta

# import "objects" from "this" project
from __init__ import db  # Key Flask objects 
# API endpoints
from api.user import user_api 
from api.pfp import pfp_api
from api.nestImg import nestImg_api # Justin added this, custom format for his website
from api.post import post_api
from api.channel import channel_api
from api.group import group_api
from api.section import section_api
from api.nestPost import nestPost_api # Justin added this, custom format for his website
from api.messages_api import messages_api # Adi added this, messages for his website
from api.carChat import carChat_api
from api.carPost import carPost_api
from api.student import student_api
from api.vin import vin_api
from api.chatBot import chatbot_api
from api.carComments import carComments_api
from api.userCars import userCars_api
from api.mechanicsTips import mechanicsTips_api
from api.vinStore import vinStore_api
from api.favorites import itemStore_api
from api.vote import vote_api

# database Initialization functions
from model.carChat import carChat
from model.mechanicsTips import MechanicsTip
from model.user import User, initUsers
from model.section import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.nestPost import NestPost, initNestPosts # Justin added this, custom format for his website
from model.vote import Vote, initVotes
from model.carPost import CarPost
from model.vehicle import Vehicle, initVehicles
from model.listings import UserItem, initDefaultUser
from model.carComments import CarComments

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# Basic CORS configuration
CORS(app)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///connectlit.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        # If there's an error, try to recreate the database
        try:
            db.drop_all()
            db.create_all()
            print("Database recreated successfully")
        except Exception as e:
            print(f"Error recreating database: {str(e)}")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Simple error handler
@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f"Error: {str(error)}")
    return jsonify({'error': 'An error occurred'}), 500

# Basic request handling
@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        return '', 200

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Get credentials from request
            if request.is_json:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
            else:
                username = request.form.get('username')
                password = request.form.get('password')
            
            # Validate credentials
            if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
            
            user = User.query.filter_by(_name=username).first()
            if not user or not user.is_password(password):
                return jsonify({'error': 'Invalid username or password'}), 401
            
            # Generate token
            token = generate_token(user)
            if not token:
                return jsonify({'error': 'Failed to generate token'}), 500
            
            # Prepare response
            response_data = {
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user._name
                }
            }
            
            # Handle API requests
            if request.is_json or request.headers.get('Accept') == 'application/json':
                response = jsonify(response_data)
                response.headers['Authorization'] = f'Bearer {token}'
                return response
            
            # Handle web requests
            response = redirect(request.form.get('next') or url_for('index'))
            response.set_cookie('jwt_token', token, httponly=True, secure=True, samesite='None')
            return response
            
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            return jsonify({'error': 'An error occurred during login'}), 500
    
    return render_template('login.html', next=request.args.get('next'))

# Register blueprints
app.register_blueprint(user_api)
app.register_blueprint(pfp_api)
app.register_blueprint(post_api)
app.register_blueprint(channel_api)
app.register_blueprint(group_api)
app.register_blueprint(section_api)
app.register_blueprint(carChat_api)
app.register_blueprint(nestPost_api)
app.register_blueprint(nestImg_api)
app.register_blueprint(vote_api)
app.register_blueprint(carPost_api)
app.register_blueprint(student_api)
app.register_blueprint(vin_api)
app.register_blueprint(chatbot_api)
app.register_blueprint(carComments_api)
app.register_blueprint(userCars_api)
app.register_blueprint(mechanicsTips_api)
app.register_blueprint(vinStore_api)
app.register_blueprint(itemStore_api)
app.register_blueprint(messages_api)

# Run the application
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8080")


# @app.route('/api/mechanicsTips', methods=['GET'])
# def get_mechanic_tip():
#     make = request.args.get('make')
#     model = request.args.get('model')
#     year = request.args.get('year')
#     issue = request.args.get('issue')

#     if not make or not model or not year or not issue:
#         return jsonify({'message': 'Missing required parameters'}), 400

#     tip = MechanicsTip.query.filter_by(_make=make, _model=model, _year=year, _issue=issue).first()

#     if tip:
#         return jsonify(tip.read())
#     else:
#         return jsonify({'message': 'Tip not found'}), 404


