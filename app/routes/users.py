"""User management routes (admin only)."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app import db
from app.models import User
from app.schemas import UserSchema, UserCreateSchema, UserUpdateSchema
from app.middleware.auth import admin_required
from app.utils.decorators import validate_json, paginated
from app.utils.helpers import paginate_query

bp = Blueprint('users', __name__, url_prefix='/api/users')

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()


@bp.route('', methods=['GET'])
@admin_required
@paginated(default_per_page=20, max_per_page=100)
def list_users(user, page, per_page):
    """List all users (paginated)."""
    query = User.query.order_by(User.created_at.desc())
    
    # Filter by role if specified
    role = request.args.get('role')
    if role in ['admin', 'user']:
        query = query.filter_by(role=role)
    
    # Filter by active status if specified
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')
    
    # Paginate
    result = paginate_query(query, page=page, per_page=per_page)
    
    return jsonify({
        'users': users_schema.dump(result['items']),
        'pagination': {
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages']
        }
    }), 200


@bp.route('', methods=['POST'])
@admin_required
@validate_json
def create_user(user):
    """Create a new user (admin only)."""
    try:
        # Validate input
        data = user_create_schema.load(request.json)
        
        # Import service to avoid circular import
        from app.services.auth_service import AuthService
        
        # Create user
        new_user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number'),
            role=data.get('role', 'user')
        )
        
        return jsonify({
            'message': 'User created successfully',
            'user': user_schema.dump(new_user)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user, user_id):
    """Get user by ID."""
    target_user = db.session.get(User, user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user_schema.dump(target_user)), 200


@bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
@validate_json
def update_user(user, user_id):
    """Update user."""
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input
        data = user_update_schema.load(request.json)
        
        # Update fields
        if 'first_name' in data:
            target_user.first_name = data['first_name']
        if 'last_name' in data:
            target_user.last_name = data['last_name']
        if 'phone_number' in data:
            target_user.phone_number = data['phone_number']
        if 'is_active' in data:
            target_user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_schema.dump(target_user)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400


@bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def deactivate_user(user, user_id):
    """Deactivate user (soft delete)."""
    target_user = db.session.get(User, user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent deactivating self
    if target_user.id == user.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    target_user.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'User deactivated successfully'}), 200
