"""Custom decorators."""
from functools import wraps
from flask import request, jsonify


def validate_json(fn):
    """Decorator to validate that request contains JSON."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return fn(*args, **kwargs)
    return wrapper


def paginated(default_per_page=20, max_per_page=100):
    """Decorator to add pagination parameters to route."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', default_per_page))
                per_page = min(per_page, max_per_page)
                page = max(1, page)
            except ValueError:
                return jsonify({'error': 'Invalid pagination parameters'}), 400
            
            kwargs['page'] = page
            kwargs['per_page'] = per_page
            return fn(*args, **kwargs)
        return wrapper
    return decorator
