"""Authentication middleware and decorators."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User
from app import db


def auth_required(fn):
    """Decorator to require authentication for a route."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Get user from database
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.is_active:
                return jsonify({'error': 'User account is inactive'}), 403
            
            # Pass user to route function
            return fn(user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    
    return wrapper


def admin_required(fn):
    """Decorator to require admin role for a route."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Get user from database
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.is_active:
                return jsonify({'error': 'User account is inactive'}), 403
            
            if not user.is_admin():
                return jsonify({'error': 'Admin access required'}), 403
            
            # Pass user to route function
            return fn(user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    
    return wrapper


def optional_auth(fn):
    """Decorator for optional authentication (doesn't fail if no auth provided)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            
            user = None
            if user_id:
                user = db.session.get(User, user_id)
                if user and not user.is_active:
                    user = None
            
            # Pass user (or None) to route function
            return fn(user, *args, **kwargs)
        except Exception:
            # If token is invalid but optional, pass None
            return fn(None, *args, **kwargs)
    
    return wrapper
