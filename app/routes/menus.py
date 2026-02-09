"""Menu and menu item routes."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from app import db
from app.models import Menu, MenuItem, Restaurant
from app.schemas import (
    MenuSchema, MenuCreateSchema, MenuUpdateSchema,
    MenuItemSchema, MenuItemCreateSchema, MenuItemUpdateSchema
)
from app.services.menu_service import MenuService
from app.middleware.auth import auth_required, admin_required
from app.utils.decorators import validate_json

bp = Blueprint('menus', __name__, url_prefix='/api/menus')

menu_schema = MenuSchema()
menus_schema = MenuSchema(many=True)
menu_create_schema = MenuCreateSchema()
menu_update_schema = MenuUpdateSchema()
menu_item_schema = MenuItemSchema()
menu_items_schema = MenuItemSchema(many=True)
menu_item_create_schema = MenuItemCreateSchema()
menu_item_update_schema = MenuItemUpdateSchema()


@bp.route('', methods=['GET'])
@auth_required
def list_menus(user):
    """List menus with optional filters."""
    query = Menu.query.filter_by(is_active=True)
    
    # Filter by restaurant
    restaurant_id = request.args.get('restaurant_id')
    if restaurant_id:
        query = query.filter_by(restaurant_id=int(restaurant_id))
    
    # Filter by date range
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(Menu.available_until >= date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(Menu.available_from <= date_to_obj)
    
    menus = query.order_by(Menu.available_from).all()
    
    return jsonify({
        'menus': menus_schema.dump(menus)
    }), 200


@bp.route('/available', methods=['GET'])
@auth_required
def get_available_menus(user):
    """Get menus available for a specific date."""
    # Get date from query params (default to today)
    target_date = request.args.get('date')
    
    menus = MenuService.get_available_menus(target_date)
    
    return jsonify({
        'menus': menus_schema.dump(menus),
        'date': target_date or datetime.now().date().isoformat()
    }), 200


@bp.route('', methods=['POST'])
@admin_required
@validate_json
def create_menu(user):
    """Create a new menu (admin only)."""
    try:
        # Validate input
        data = menu_create_schema.load(request.json)
        
        # Verify restaurant exists
        restaurant = db.session.get(Restaurant, data['restaurant_id'])
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        # Validate date range
        MenuService.validate_menu_date_range(
            data['available_from'],
            data['available_until'],
            data['restaurant_id']
        )
        
        # Create menu
        menu = Menu(**data)
        db.session.add(menu)
        db.session.commit()
        
        return jsonify({
            'message': 'Menu created successfully',
            'menu': menu_schema.dump(menu)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:menu_id>', methods=['GET'])
@auth_required
def get_menu(user, menu_id):
    """Get menu with items."""
    result = MenuService.get_menu_with_items(menu_id)
    if not result:
        return jsonify({'error': 'Menu not found'}), 404
    
    menu, items = result
    
    # Check access
    if not user.is_admin() and not menu.is_active:
        return jsonify({'error': 'Menu not found'}), 404
    
    menu_data = menu.to_dict(include_items=False)
    menu_data['items'] = menu_items_schema.dump(items)
    
    return jsonify(menu_data), 200


@bp.route('/<int:menu_id>', methods=['PUT'])
@admin_required
@validate_json
def update_menu(user, menu_id):
    """Update menu (admin only)."""
    try:
        menu = db.session.get(Menu, menu_id)
        if not menu:
            return jsonify({'error': 'Menu not found'}), 404
        
        # Validate input
        data = menu_update_schema.load(request.json)
        
        # Update fields
        for key, value in data.items():
            setattr(menu, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Menu updated successfully',
            'menu': menu_schema.dump(menu)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400


@bp.route('/<int:menu_id>', methods=['DELETE'])
@admin_required
def delete_menu(user, menu_id):
    """Delete menu (admin only)."""
    menu = db.session.get(Menu, menu_id)
    if not menu:
        return jsonify({'error': 'Menu not found'}), 404
    
    menu.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Menu deleted successfully'}), 200


# Menu Item Routes

@bp.route('/<int:menu_id>/items', methods=['POST'])
@admin_required
@validate_json
def create_menu_item(user, menu_id):
    """Add item to menu (admin only)."""
    try:
        # Verify menu exists
        menu = db.session.get(Menu, menu_id)
        if not menu:
            return jsonify({'error': 'Menu not found'}), 404
        
        # Validate input
        data = menu_item_create_schema.load(request.json)
        
        # Create menu item
        menu_item = MenuItem(menu_id=menu_id, **data)
        db.session.add(menu_item)
        db.session.commit()
        
        return jsonify({
            'message': 'Menu item created successfully',
            'item': menu_item_schema.dump(menu_item)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400


@bp.route('/items/<int:item_id>', methods=['PUT'])
@admin_required
@validate_json
def update_menu_item(user, item_id):
    """Update menu item (admin only)."""
    try:
        menu_item = db.session.get(MenuItem, item_id)
        if not menu_item:
            return jsonify({'error': 'Menu item not found'}), 404
        
        # Validate input
        data = menu_item_update_schema.load(request.json)
        
        # Update fields
        for key, value in data.items():
            setattr(menu_item, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Menu item updated successfully',
            'item': menu_item_schema.dump(menu_item)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400


@bp.route('/items/<int:item_id>', methods=['DELETE'])
@admin_required
def delete_menu_item(user, item_id):
    """Delete menu item (admin only)."""
    menu_item = db.session.get(MenuItem, item_id)
    if not menu_item:
        return jsonify({'error': 'Menu item not found'}), 404
    
    menu_item.is_available = False
    db.session.commit()
    
    return jsonify({'message': 'Menu item deleted successfully'}), 200
