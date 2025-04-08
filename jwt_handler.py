import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from model.user import User

# JWT Configuration
JWT_SECRET_KEY = 'your-secret-key'  # Change this in production
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION_DAYS = 1

def generate_token(user):
    """Generate a JWT token for the given user."""
    payload = {
        'id': user.id,
        'username': user._name,
        'role': user._role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=TOKEN_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token):
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
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
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            if request.is_json:
                return jsonify({'message': 'Invalid or expired token'}), 401
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        user = User.query.get(payload['id'])
        if not user:
            if request.is_json:
                return jsonify({'message': 'User not found'}), 401
            return jsonify({'message': 'User not found'}), 401
        
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