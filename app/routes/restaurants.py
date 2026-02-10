"""Restaurant routes."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from app import db
from app.models import Restaurant, RestaurantAvailability, Menu, MotdOption
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


@bp.route('/available', methods=['GET'])
@auth_required
def get_available_restaurants(user):
    """List restaurants available for a specific date, including their menu content."""
    target_date = request.args.get('date')
    if target_date:
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    else:
        from datetime import date
        target_date_obj = date.today()

    weekday = target_date_obj.weekday()  # 0=Mon
    if weekday > 4:
        return jsonify({'date': target_date_obj.isoformat(), 'restaurants': []}), 200

    available_ids = [
        r.restaurant_id
        for r in RestaurantAvailability.query.filter_by(weekday=weekday, is_available=True).all()
    ]
    if not available_ids:
        return jsonify({'date': target_date_obj.isoformat(), 'restaurants': []}), 200

    restaurants = Restaurant.query.filter(Restaurant.id.in_(available_ids), Restaurant.is_active.is_(True)).all()

    # Find the (single) active menu for each restaurant that is valid for date
    menus = Menu.query.filter(
        Menu.restaurant_id.in_(available_ids),
        Menu.is_active.is_(True),
        Menu.available_from <= target_date_obj,
        Menu.available_until >= target_date_obj,
    ).all()
    menu_by_restaurant = {m.restaurant_id: m for m in menus}

    motd_rows = MotdOption.query.filter(
        MotdOption.restaurant_id.in_(available_ids),
        MotdOption.weekday == weekday,
    ).all()
    motd_by_restaurant = {m.restaurant_id: m.option_text for m in motd_rows}

    result = []
    for r in sorted(restaurants, key=lambda x: x.name.lower()):
        menu = menu_by_restaurant.get(r.id)
        result.append({
            'restaurant': restaurant_schema.dump(r),
            'menu': menu.to_dict(include_items=False) if menu else None,
            'motd_option': motd_by_restaurant.get(r.id),
        })

    return jsonify({'date': target_date_obj.isoformat(), 'restaurants': result}), 200


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
        db.session.flush()

        # Default availability: Mon-Fri
        for w in range(5):
            db.session.add(RestaurantAvailability(restaurant_id=restaurant.id, weekday=w, is_available=True))
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
