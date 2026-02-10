"""Menu and menu item routes."""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
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

ALLOWED_MENU_UPLOAD_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp'}


def _save_menu_upload(file_storage):
    original_name = file_storage.filename or ''
    ext = os.path.splitext(original_name.lower())[1]
    if ext not in ALLOWED_MENU_UPLOAD_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext or 'unknown'}")

    upload_dir = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
    os.makedirs(upload_dir, exist_ok=True)

    safe_original = secure_filename(original_name) or f"menu{ext}"
    filename = f"{uuid.uuid4().hex}_{safe_original}"
    file_path = os.path.join(upload_dir, filename)
    file_storage.save(file_path)

    return {
        "path": filename,
        "mime": file_storage.mimetype,
        "name": original_name,
    }


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

        # Enforce: one active menu per restaurant (keep history by deactivating previous)
        Menu.query.filter_by(restaurant_id=data['restaurant_id'], is_active=True).update(
            {"is_active": False},
            synchronize_session=False,
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


@bp.route('/with-content', methods=['POST'])
@admin_required
def create_menu_with_content(user):
    """
    Create a new menu (admin only) with optional text and/or uploaded file.

    Accepts multipart form-data:
      - restaurant_id (required)
      - name (required)
      - description (optional)
      - available_from (optional, YYYY-MM-DD; default today)
      - available_until (optional, YYYY-MM-DD; default today+30)
      - menu_text (optional)
      - menu_file (optional file: pdf/image)
    """
    try:
        restaurant_id = request.form.get('restaurant_id', type=int)
        name = (request.form.get('name') or '').strip()
        description = (request.form.get('description') or '').strip() or None
        menu_text = (request.form.get('menu_text') or '').strip() or None

        if not restaurant_id or not name:
            return jsonify({'error': 'restaurant_id and name are required'}), 400

        restaurant = db.session.get(Restaurant, restaurant_id)
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404

        from_str = request.form.get('available_from')
        until_str = request.form.get('available_until')
        available_from = datetime.strptime(from_str, '%Y-%m-%d').date() if from_str else date.today()
        # Default: effectively "forever" unless an end date is explicitly provided.
        available_until = datetime.strptime(until_str, '%Y-%m-%d').date() if until_str else date(2099, 12, 31)

        MenuService.validate_menu_date_range(available_from, available_until, restaurant_id)

        # Enforce: one active menu per restaurant (keep history by deactivating previous)
        Menu.query.filter_by(restaurant_id=restaurant_id, is_active=True).update(
            {"is_active": False},
            synchronize_session=False,
        )

        menu = Menu(
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            available_from=available_from,
            available_until=available_until,
        )

        if menu_text:
            menu.menu_text = menu_text

        file_storage = request.files.get('menu_file')
        if file_storage and file_storage.filename:
            saved = _save_menu_upload(file_storage)
            menu.menu_file_path = saved["path"]
            menu.menu_file_mime = saved["mime"]
            menu.menu_file_name = saved["name"]

        if not menu.menu_text and not menu.menu_file_path:
            return jsonify({'error': 'Provide either menu_text or a menu_file'}), 400

        db.session.add(menu)
        db.session.commit()

        return jsonify({
            'message': 'Menu created successfully',
            'menu': menu_schema.dump(menu)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.exception("Failed to create menu with content")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:menu_id>/content', methods=['PUT'])
@admin_required
def update_menu_content(user, menu_id):
    """
    Update menu content (text and/or file). Accepts multipart form-data:
      - menu_text (optional)
      - menu_file (optional)
      - clear_file (optional: 'true' to remove existing file)
    """
    menu = db.session.get(Menu, menu_id)
    if not menu:
        return jsonify({'error': 'Menu not found'}), 404

    menu_text = request.form.get('menu_text')
    if menu_text is not None:
        menu.menu_text = menu_text.strip() or None

    if (request.form.get('clear_file') or '').lower() in ('1', 'true', 'yes', 'on'):
        menu.menu_file_path = None
        menu.menu_file_mime = None
        menu.menu_file_name = None

    file_storage = request.files.get('menu_file')
    if file_storage and file_storage.filename:
        saved = _save_menu_upload(file_storage)
        menu.menu_file_path = saved["path"]
        menu.menu_file_mime = saved["mime"]
        menu.menu_file_name = saved["name"]

    db.session.commit()
    return jsonify({'message': 'Menu content updated', 'menu': menu_schema.dump(menu)}), 200


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
