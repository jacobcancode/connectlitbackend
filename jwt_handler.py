import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, redirect, url_for
from model.user import User

def generate_token(user):
    """Generate a JWT token for the given user."""
    try:
        # Simple payload with essential data
        payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        # Generate token using app's secret key
        token = jwt.encode(
            payload=payload,
            key=current_app.secret_key,
            algorithm='HS256'
        )
        return token
    except Exception as e:
        current_app.logger.error(f"Token generation error: {str(e)}")
        return None

def decode_token(token):
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            jwt=token,
            key=current_app.secret_key,
            algorithms=['HS256']
        )
        return payload
    except Exception as e:
        current_app.logger.error(f"Token decoding error: {str(e)}")
        return None

def get_token_from_request():
    """Extract token from request headers or cookies."""
    # Check Authorization header first
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Then check cookies
    return request.cookies.get('jwt_token')

def token_required(f):
    """Decorator to require JWT token for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
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
    
    return User.query.get(payload['user_id']) 