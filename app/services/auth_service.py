"""Authentication service."""
from datetime import datetime, timedelta
from flask import current_app
from flask_jwt_extended import create_access_token
from app import db
from app.models import User, Session
from app.utils.validators import validate_email, validate_password


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def register_user(email, password, first_name, last_name, phone_number=None, role='user'):
        """Register a new user."""
        # Validate email
        if not validate_email(email):
            raise ValueError('Invalid email format')
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            raise ValueError(message)
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError('User with this email already exists')
        
        # Create new user
        user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def login_user(email, password):
        """Authenticate user and create session."""
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError('Invalid email or password')
        
        # Check if user is active
        if not user.is_active:
            raise ValueError('User account is inactive')
        
        # Verify password
        if not user.check_password(password):
            raise ValueError('Invalid email or password')
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        # Create session record
        expires_at = datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        session = Session(
            user_id=user.id,
            token=access_token,
            expires_at=expires_at
        )
        
        db.session.add(session)
        db.session.commit()
        
        return {
            'user': user,
            'access_token': access_token,
            'expires_at': expires_at
        }
    
    @staticmethod
    def logout_user(token):
        """Logout user by removing session."""
        session = Session.query.filter_by(token=token).first()
        if session:
            db.session.delete(session)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def change_password(user, current_password, new_password):
        """Change user password."""
        # Verify current password
        if not user.check_password(current_password):
            raise ValueError('Current password is incorrect')
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            raise ValueError(message)
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return True
    
    @staticmethod
    def update_profile(user, first_name=None, last_name=None, phone_number=None):
        """Update user profile."""
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone_number is not None:
            user.phone_number = phone_number
        
        db.session.commit()
        return user
    
    @staticmethod
    def cleanup_expired_sessions():
        """Remove expired sessions from database."""
        expired_sessions = Session.query.filter(Session.expires_at < datetime.utcnow()).all()
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()
        return len(expired_sessions)
