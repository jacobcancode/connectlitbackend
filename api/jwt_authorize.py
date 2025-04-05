from flask import request, session, current_app, g
from functools import wraps
from model.user import User

def token_required(roles=None):
    """
    Guard API endpoints that require authentication using Flask sessions.
    """
    def decorator(func_to_guard):
        @wraps(func_to_guard)
        def decorated(*args, **kwargs):
            # Check if user is logged in
            if 'user_id' not in session:
                return {
                    "message": "Not logged in",
                    "error": "Unauthorized"
                }, 401

            try:
                # Get user from session
                current_user = User.query.get(session['user_id'])
                if not current_user:
                    return {
                        "message": "User not found",
                        "error": "Unauthorized"
                    }, 401

                if roles and current_user.role not in roles:
                    return {
                        "message": "User does not have the required role",
                        "error": "Forbidden"
                    }, 403
                    
                # Authentication success, set the current_user in the global context
                g.current_user = current_user
                return func_to_guard(*args, **kwargs)

            except Exception as e:
                return {
                    "message": "An error occurred",
                    "error": str(e)
                }, 500

        return decorated
    return decorator