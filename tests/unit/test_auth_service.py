"""Unit tests for authentication service."""
import pytest
from app.services.auth_service import AuthService
from app.models import User


class TestAuthService:
    """Test authentication service."""
    
    def test_register_user_success(self, app, db_session):
        """Test successful user registration."""
        with app.app_context():
            user = AuthService.register_user(
                email='newuser@test.com',
                password='NewUser123!',
                first_name='New',
                last_name='User',
                phone_number='+1234567890'
            )
            
            assert user.id is not None
            assert user.email == 'newuser@test.com'
            assert user.first_name == 'New'
            assert user.last_name == 'User'
            assert user.role == 'user'
            assert user.is_active is True
            assert user.password_hash != 'NewUser123!'  # Password should be hashed
    
    def test_register_user_duplicate_email(self, app, db_session, regular_user):
        """Test registration with duplicate email fails."""
        with app.app_context():
            with pytest.raises(ValueError, match='User with this email already exists'):
                AuthService.register_user(
                    email='user@test.com',  # Already exists
                    password='Password123!',
                    first_name='Duplicate',
                    last_name='User'
                )
    
    def test_register_user_invalid_email(self, app, db_session):
        """Test registration with invalid email fails."""
        with app.app_context():
            with pytest.raises(ValueError, match='Invalid email format'):
                AuthService.register_user(
                    email='not-an-email',
                    password='Password123!',
                    first_name='Test',
                    last_name='User'
                )
    
    def test_register_user_weak_password(self, app, db_session):
        """Test registration with weak password fails."""
        with app.app_context():
            with pytest.raises(ValueError, match='Password must'):
                AuthService.register_user(
                    email='test@test.com',
                    password='weak',  # Too short, no uppercase, no numbers
                    first_name='Test',
                    last_name='User'
                )
    
    def test_login_success(self, app, db_session, regular_user):
        """Test successful login."""
        with app.app_context():
            result = AuthService.login_user('user@test.com', 'User123!')
            
            assert 'user' in result
            assert 'access_token' in result
            assert 'expires_at' in result
            assert result['user'].email == 'user@test.com'
            assert len(result['access_token']) > 0
    
    def test_login_invalid_email(self, app, db_session):
        """Test login with non-existent email."""
        with app.app_context():
            with pytest.raises(ValueError, match='Invalid email/username or password'):
                AuthService.login_user('nonexistent@test.com', 'Password123!')
    
    def test_login_wrong_password(self, app, db_session, regular_user):
        """Test login with wrong password."""
        with app.app_context():
            with pytest.raises(ValueError, match='Invalid email/username or password'):
                AuthService.login_user('user@test.com', 'WrongPassword!')
    
    def test_login_inactive_user(self, app, db_session, regular_user):
        """Test login with inactive user."""
        with app.app_context():
            # Refetch user in this context and deactivate
            from app.models import User
            user = User.query.filter_by(email='user@test.com').first()
            user.is_active = False
            db_session.commit()

            with pytest.raises(ValueError, match='User account is inactive'):
                AuthService.login_user('user@test.com', 'User123!')
    
    def test_change_password_success(self, app, db_session, regular_user):
        """Test successful password change."""
        with app.app_context():
            result = AuthService.change_password(
                regular_user,
                'User123!',
                'NewPassword123!'
            )
            
            assert result is True
            assert regular_user.check_password('NewPassword123!')
            assert not regular_user.check_password('User123!')
    
    def test_change_password_wrong_current(self, app, db_session, regular_user):
        """Test password change with wrong current password."""
        with app.app_context():
            with pytest.raises(ValueError, match='Current password is incorrect'):
                AuthService.change_password(
                    regular_user,
                    'WrongPassword!',
                    'NewPassword123!'
                )
    
    def test_change_password_weak_new(self, app, db_session, regular_user):
        """Test password change with weak new password."""
        with app.app_context():
            with pytest.raises(ValueError, match='Password must'):
                AuthService.change_password(
                    regular_user,
                    'User123!',
                    'weak'
                )
    
    def test_update_profile(self, app, db_session, regular_user):
        """Test profile update."""
        with app.app_context():
            updated_user = AuthService.update_profile(
                regular_user,
                first_name='Updated',
                last_name='Name',
                phone_number='+9999999999'
            )
            
            assert updated_user.first_name == 'Updated'
            assert updated_user.last_name == 'Name'
            assert updated_user.phone_number == '+9999999999'
