import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify, current_app, redirect, url_for
from model.user import User

def generate_token(user):
    """Generate a JWT token for the given user."""
    try:
        payload = {
            'id': user.id,
            'username': user._name,
            'role': user._role,
            'exp': datetime.datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
        # Generate token with proper error handling
        token = jwt.encode(
            payload=payload,
            key=current_app.config['JWT_SECRET_KEY'],
            algorithm=current_app.config['JWT_ALGORITHM']
        )
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token
    except Exception as e:
        current_app.logger.error(f"Error generating token: {str(e)}")
        return None

def decode_token(token):
    """Decode and validate a JWT token."""
    try:
        # Decode token with proper error handling
        payload = jwt.decode(
            jwt=token,
            key=current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config['JWT_ALGORITHM']]
        )
        return payload
    except jwt.ExpiredSignatureError:
        current_app.logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        current_app.logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Error decoding token: {str(e)}")
        return None

def get_token_from_request():
    """Extract token from request headers or cookies."""
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Check cookies
    return request.cookies.get('jwt_token')

def token_required(f):
    """Decorator to require JWT token for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            if request.is_json:
                return jsonify({'message': 'Token is missing'}), 401
            return redirect(url_for('login'))
        
        payload = decode_token(token)
        if not payload:
            if request.is_json:
                return jsonify({'message': 'Invalid or expired token'}), 401
            return redirect(url_for('login'))
        
        user = User.query.get(payload['id'])
        if not user:
            if request.is_json:
                return jsonify({'message': 'User not found'}), 401
            return redirect(url_for('login'))
        
        return f(user, *args, **kwargs)
    return decorated

def get_current_user():
    """Get the current user from the JWT token."""
    token = get_token_from_request()
    if not token:
        return None
    
    payload = decode_token(token)
    if not payload:
        return None
    
    return User.query.get(payload['id']) 