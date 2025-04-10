import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime, timedelta
from __init__ import app
from api.jwt_authorize import token_required
from model.user import User
import json

# Create a Blueprint for the user API
user_api = Blueprint('user_api', __name__, url_prefix='/api')

# Create an Api object and associate it with the Blueprint
# API docs: https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(user_api)

class UserAPI:
    """
    Define the API endpoints for the User model.
    """
    class _BULK_CRUD(Resource):
        """
        Users API operation for bulk Create and Read.
        """

        def post(self):
            """
            Handle bulk user creation by sending POST requests to the single user endpoint.
            """
            users = request.get_json()

            if not isinstance(users, list):
                return {'message': 'Expected a list of user data'}, 400

            results = {'errors': [], 'success_count': 0, 'error_count': 0}

            with current_app.test_client() as client:
                for user in users:
                    # Set a default password as we don't have it for bulk creation
                    user["password"] = app.config['DEFAULT_PASSWORD']

                    # Simulate a POST request to the single user creation endpoint
                    response = client.post('/api/user', json=user)

                    if response.status_code == 200:
                        results['success_count'] += 1
                    else:
                        results['errors'].append(response.get_json())
                        results['error_count'] += 1

            return jsonify(results)
        
        @token_required()
        def get(self):
            """
            Retrieve all users.
            """
            current_user = g.current_user
            users = User.query.all()  # extract all users from the database

            # Prepare a JSON list of user dictionaries
            json_ready = []
            for user in users:
                user_data = user.read()
                if current_user.role == 'Admin' or current_user.id == user.id:
                    user_data['access'] = ['rw']  # read-write access control
                else:
                    user_data['access'] = ['ro']  # read-only access control
                json_ready.append(user_data)

            return jsonify(json_ready)

    class _CRUD(Resource):
        """
        Users API operation for Create, Read, Update, Delete.
        """

        def post(self):
            """
            Create a new user.
            """
            try:
                body = request.get_json()
                if not body:
                    return {
                        "message": "Please provide user details",
                        "error": "Bad request"
                    }, 400

                # Validate name
                name = body.get('name')
                if name is None or len(name) < 2:
                    return {
                        "message": "Name is missing or less than 2 characters",
                        "error": "Validation error"
                    }, 400

                # Validate uid
                uid = body.get('uid')
                if uid is None or len(uid) < 2:
                    return {
                        "message": "User ID is missing or less than 2 characters",
                        "error": "Validation error"
                    }, 400

                # Validate password
                password = body.get('password')
                if password is None or len(password) < 6:
                    return {
                        "message": "Password is missing or less than 6 characters",
                        "error": "Validation error"
                    }, 400

                # Check if user already exists
                existing_user = User.query.filter_by(_uid=uid).first()
                if existing_user:
                    return {
                        "message": "User ID already exists",
                        "error": "Duplicate error"
                    }, 409

                # Setup minimal USER OBJECT
                user_obj = User(name=name, uid=uid)

                # Add user to database
                user = user_obj.create(body)
                if not user:
                    return {
                        "message": "Failed to create user",
                        "error": "Database error"
                    }, 500

                # Create response with CORS headers
                resp = jsonify(user.read())
                resp.headers.add('Access-Control-Allow-Origin', 'https://jacobcancode.github.io')
                resp.headers.add('Access-Control-Allow-Credentials', 'true')
                return resp

            except Exception as e:
                return {
                    "message": "An error occurred during signup",
                    "error": str(e)
                }, 500
        
        @token_required()
        def get(self): 
            user = g.current_user
            user_data = user.read()
            resp = jsonify(user_data)
            resp.headers.add('Access-Control-Allow-Origin', 'https://jacobcancode.github.io')
            resp.headers.add('Access-Control-Allow-Credentials', 'true')
            return resp
    @token_required()
    def put(self):
        """
        Update a user.
        """
        current_user = g.current_user
        body = request.get_json()

        # Admin-specific update handling
        if current_user.role == 'Admin':
            uid = body.get('uid')
            user = current_user if uid is None or uid == current_user.uid else User.query.filter_by(_uid=uid).first()
            if not user:
                return {'message': f'User {uid} not found'}, 404

            user.update(body)
            resp = jsonify(user.read())
            resp.headers.add('Access-Control-Allow-Origin', 'https://jacobcancode.github.io')
            resp.headers.add('Access-Control-Allow-Credentials', 'true')
            return resp

    @token_required("Admin")
    def delete(self):
            """
            Delete a user.
            """
            body = request.get_json()
            uid = body.get('uid')
            user = User.query.filter_by(_uid=uid).first()
            if user is None:
                return {'message': f'User {uid} not found'}, 404
            json = user.read()
            user.delete()
            return f"Deleted user: {json}", 204  # use 200 to test with Postman

class _Security(Resource):
    """
    Security-related API operations.
    """

    def post(self):
        """
        Authenticate a user and generate a JWT token.
        """
        try:
            body = request.get_json()
            if not body:
                return {
                    "message": "Please provide user details",
                    "error": "Bad request"
                }, 400

            # Get Data
            uid = body.get('uid')
            if uid is None:
                return {
                    "message": "User ID is missing",
                    "error": "Validation error"
                }, 401
            password = body.get('password')
            if not password:
                return {
                    "message": "Password is missing",
                    "error": "Validation error"
                }, 401

            # Find user
            user = User.query.filter_by(_uid=uid).first()
            if user is None:
                return {
                    "message": "User not found",
                    "error": "Authentication error"
                }, 401

            if not user.is_password(password):
                return {
                    "message": "Invalid password",
                    "error": "Authentication error"
                }, 401

            # Generate token
            token = jwt.encode(
                {
                    "_uid": user._uid,
                    "exp": datetime.utcnow() + timedelta(seconds=3600)
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            # Return both token and user data in JSON
            response_data = {
                "message": f"Authentication for {user._uid} successful",
                "token": token,
                "user": user.read()
            }

            # ✅ Use jsonify for proper headers and encoding
            resp = jsonify(response_data)

            # ✅ Set the token as an HttpOnly cookie
            resp.set_cookie(
                current_app.config["JWT_TOKEN_NAME"],
                token,
                max_age=3600,
                secure=True,
                httponly=True,
                path='/',
                samesite='None',
                domain='.github.io'
            )

            # ✅ CORS headers for GitHub Pages
            resp.headers.add('Access-Control-Allow-Origin', 'https://jacobcancode.github.io')
            resp.headers.add('Access-Control-Allow-Credentials', 'true')
            resp.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            resp.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')

            return resp

        except Exception as e:
            print(f"Login error: {str(e)}")
            return {
                "message": "An error occurred during login",
                "error": str(e)
            }, 500

    @token_required()
    def delete(self):
        """
        Invalidate the current user's token by setting its expiry to 0.
        """
        current_user = g.current_user
        try:
            token = jwt.encode(
                {"_uid": current_user._uid, "exp": datetime.utcnow()},
                current_app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            resp = Response("Token invalidated successfully")
            resp.set_cookie(
                current_app.config["JWT_TOKEN_NAME"],
                token,
                max_age=0,
                secure=True,
                httponly=True,
                path='/',
                samesite='None'
            )
            return resp
        except Exception as e:
            return {
                "message": "Failed to invalidate token",
                "error": str(e)
            }, 500
    class _ID(Resource):  # Individual identification API operation
        @token_required()
        def get(self):
            ''' Retrieve the current user from the token_required authentication check '''
            current_user = g.current_user
            ''' Return the current user as a json object '''
            return jsonify(current_user.read())

# Register the API resources with the Blueprint
api.add_resource(UserAPI._ID, '/id')
api.add_resource(UserAPI._BULK_CRUD, '/users')
api.add_resource(UserAPI._CRUD, '/user')
api.add_resource(UserAPI._Security, '/authenticate')