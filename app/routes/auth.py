"""Authentication routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from marshmallow import ValidationError
from app.services.auth_service import AuthService
from app.schemas import UserSchema, UserCreateSchema, LoginSchema, ChangePasswordSchema, UserUpdateSchema
from app.middleware.auth import auth_required
from app.utils.decorators import validate_json
from app import db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

user_schema = UserSchema()
user_create_schema = UserCreateSchema()
login_schema = LoginSchema()
change_password_schema = ChangePasswordSchema()
user_update_schema = UserUpdateSchema()


@bp.route('/register', methods=['POST'])
@validate_json
def register():
    """Register a new user."""
    try:
        # Validate input
        data = user_create_schema.load(request.json)
        
        # Register user
        user = AuthService.register_user(
            username=data.get('username'),
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number'),
            role=data.get('role', 'user')
        )

        if data.get('birth_date') is not None:
            user.birth_date = data['birth_date']
            db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(user)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500


@bp.route('/login', methods=['POST'])
@validate_json
def login():
    """Login user and return JWT token."""
    try:
        # Validate input
        data = login_schema.load(request.json)

        identifier = data.get('identifier') or data.get('email') or data.get('username')

        # Authenticate user
        result = AuthService.login_user(identifier, data['password'])
        
        return jsonify({
            'message': 'Login successful',
            'user': user_schema.dump(result['user']),
            'access_token': result['access_token'],
            'expires_at': result['expires_at'].isoformat()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500


@bp.route('/logout', methods=['POST'])
@auth_required
def logout(user):
    """Logout user by invalidating token."""
    try:
        # Get token from request
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Logout user
        AuthService.logout_user(token)
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'message': str(e)}), 500


@bp.route('/me', methods=['GET'])
@auth_required
def get_current_user(user):
    """Get current user profile."""
    return jsonify(user_schema.dump(user)), 200


@bp.route('/me', methods=['PUT'])
@auth_required
@validate_json
def update_profile(user):
    """Update current user profile."""
    try:
        # Validate input
        data = user_update_schema.load(request.json)
        
        # Update profile
        updated_user = AuthService.update_profile(
            user=user,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            birth_date=data.get('birth_date') if 'birth_date' in data else None
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user_schema.dump(updated_user)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Update failed', 'message': str(e)}), 500


@bp.route('/change-password', methods=['POST'])
@auth_required
@validate_json
def change_password(user):
    """Change user password."""
    try:
        # Validate input
        data = change_password_schema.load(request.json)
        
        # Change password
        AuthService.change_password(
            user=user,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Password change failed', 'message': str(e)}), 500
