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
app.config['JWT_TOKEN_NAME'] = os.environ.get('JWT_TOKEN_NAME', 'jwt_token')

def generate_token(user):
    """
    Generate a JWT token for the given user.
    
    Args:
        user (User): The user object to generate the token for.
        
    Returns:
        str: The generated JWT token.
    """
    try:
        # Create the token payload
        payload = {
            'user_id': user.id,
            'username': user._uid,
            'exp': datetime.datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
        
        # Generate the token
        token = jwt.encode(
            payload,
            app.config['JWT_SECRET_KEY'],
            algorithm=app.config['JWT_ALGORITHM']
        )
        
        return token
    except Exception as e:
        app.logger.error(f"Token generation error: {str(e)}")
        return None

def token_required(f):
    """
    Decorator to require a valid JWT token for protected routes.
    
    Args:
        f (function): The route function to protect.
        
    Returns:
        function: The wrapped route function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Get token from cookie if not in header
        if not token:
            token = request.cookies.get(app.config['JWT_TOKEN_NAME'])
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            # Decode the token
            payload = jwt.decode(
                token,
                app.config['JWT_SECRET_KEY'],
                algorithms=[app.config['JWT_ALGORITHM']]
            )
            
            # Get user from token
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 401
                
            # Add user to request context
            request.user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            app.logger.error(f"Token validation error: {str(e)}")
            return jsonify({'error': 'Token validation failed'}), 401
            
        return f(*args, **kwargs)
        
    return decorated

# Basic CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:4888",
            "http://127.0.0.1:4888",
            "https://bookconnect-832734119496.us-west1.run.app",
            "https://*.us-west1.run.app",  # Allow all subdomains of us-west1.run.app
            "https://jacobcancode.github.io",  # GitHub Pages frontend
            "https://*.github.io"  # Allow all GitHub Pages domains
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///volumes/user_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database tables
with app.app_context():
    try:
        # Check if database exists and is accessible
        db.engine.connect()
        print("Database connection successful")
        
        # Create tables if they don't exist
        db.create_all()
        print("Database tables created/verified successfully")
        
        # Initialize default data if needed
        try:
            initUsers()
            initSections()
            initGroups()
            initChannels()
            initPosts()
            initNestPosts()
            initVotes()
            initVehicles()
            initDefaultUser()
            print("Default data initialized successfully")
        except Exception as e:
            print(f"Warning: Error initializing default data: {str(e)}")
            # Continue even if default data initialization fails
            
    except Exception as e:
        print(f"Critical error: {str(e)}")
        # Don't try to recreate the database in production
        if os.environ.get('FLASK_ENV') == 'development':
            try:
                print("Attempting to recreate database in development mode...")
                db.drop_all()
                db.create_all()
                print("Database recreated successfully")
            except Exception as e:
                print(f"Error recreating database: {str(e)}")
        else:
            print("Database initialization failed in production mode")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Error loading user: {str(e)}")
        return None

# Simple error handler
@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f"Error: {str(error)}")
    app.logger.error(f"Error type: {type(error)}")
    app.logger.error(f"Error args: {error.args}")
    
    # Get the current request information
    request_info = {
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
        'data': request.get_data().decode('utf-8') if request.get_data() else None,
        'args': dict(request.args),
        'form': dict(request.form) if request.form else None,
        'json': request.get_json() if request.is_json else None
    }
    app.logger.error(f"Request info: {request_info}")
    
    # Return a more detailed error response
    return jsonify({
        'error': 'An error occurred',
        'message': str(error),
        'type': type(error).__name__,
        'status_code': 500
    }), 500

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
            
            user = User.query.filter_by(_uid=username).first()
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
                    'username': user._uid,
                    'name': user._name
                }
            }
            
            # Handle API requests
            if request.is_json or request.headers.get('Accept') == 'application/json':
                response = jsonify(response_data)
                response.headers['Authorization'] = f'Bearer {token}'
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                return response
            
            # Handle web requests
            response = redirect(request.form.get('next') or url_for('index'))
            response.set_cookie(
                app.config['JWT_TOKEN_NAME'],
                token,
                httponly=True,
                secure=True,
                samesite='None'
            )
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

# Root route
@app.route('/')
def index():
    return render_template('index.html')

# Health check route
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db.engine else 'disconnected'
    })

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


