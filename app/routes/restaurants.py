"""Restaurant routes."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app import db
from app.models import Restaurant
from app.schemas import RestaurantSchema, RestaurantCreateSchema, RestaurantUpdateSchema
from app.middleware.auth import auth_required, admin_required
from app.utils.decorators import validate_json

bp = Blueprint('restaurants', __name__, url_prefix='/api/restaurants')

restaurant_schema = RestaurantSchema()
restaurants_schema = RestaurantSchema(many=True)
restaurant_create_schema = RestaurantCreateSchema()
restaurant_update_schema = RestaurantUpdateSchema()


@bp.route('', methods=['GET'])
@auth_required
def list_restaurants(user):
    """List all active restaurants."""
    # Filter by active status (default to active only)
    is_active = request.args.get('is_active', 'true')
    
    if user.is_admin():
        # Admins can see all restaurants
        if is_active.lower() == 'all':
            query = Restaurant.query
        else:
            query = Restaurant.query.filter_by(is_active=is_active.lower() == 'true')
    else:
        # Regular users only see active restaurants
        query = Restaurant.query.filter_by(is_active=True)
    
    restaurants = query.order_by(Restaurant.name).all()
    
    return jsonify({
        'restaurants': restaurants_schema.dump(restaurants)
    }), 200


@bp.route('', methods=['POST'])
@admin_required
@validate_json
def create_restaurant(user):
    """Create a new restaurant (admin only)."""
    try:
        # Validate input
        data = restaurant_create_schema.load(request.json)
        
        # Create restaurant
        restaurant = Restaurant(**data)
        
        db.session.add(restaurant)
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant created successfully',
            'restaurant': restaurant_schema.dump(restaurant)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400


@bp.route('/<int:restaurant_id>', methods=['GET'])
@auth_required
def get_restaurant(user, restaurant_id):
    """Get restaurant by ID."""
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    # Non-admins can only see active restaurants
    if not user.is_admin() and not restaurant.is_active:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    return jsonify(restaurant_schema.dump(restaurant)), 200


@bp.route('/<int:restaurant_id>', methods=['PUT'])
@admin_required
@validate_json
def update_restaurant(user, restaurant_id):
    """Update restaurant (admin only)."""
    try:
        restaurant = db.session.get(Restaurant, restaurant_id)
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        # Validate input
        data = restaurant_update_schema.load(request.json)
        
        # Update fields
        for key, value in data.items():
            setattr(restaurant, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant updated successfully',
            'restaurant': restaurant_schema.dump(restaurant)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400


@bp.route('/<int:restaurant_id>', methods=['DELETE'])
@admin_required
def deactivate_restaurant(user, restaurant_id):
    """Deactivate restaurant (soft delete, admin only)."""
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    restaurant.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Restaurant deactivated successfully'}), 200
