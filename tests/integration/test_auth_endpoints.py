"""Integration tests for authentication endpoints."""
import pytest


class TestAuthEndpoints:
    """Test authentication API endpoints."""
    
    def test_register_success(self, client, db_session):
        """Test successful registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@test.com',
            'password': 'NewUser123!',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+1234567890'
        })
        
        assert response.status_code == 201
        data = response.json
        assert 'user' in data
        assert data['user']['email'] == 'newuser@test.com'
        assert data['user']['role'] == 'user'
        assert 'password' not in data['user']
    
    def test_register_duplicate_email(self, client, regular_user):
        """Test registration with duplicate email."""
        response = client.post('/api/auth/register', json={
            'email': 'user@test.com',
            'password': 'Password123!',
            'first_name': 'Duplicate',
            'last_name': 'User'
        })
        
        assert response.status_code == 400
        assert 'already exists' in response.json['error']
    
    def test_register_invalid_data(self, client):
        """Test registration with invalid data."""
        response = client.post('/api/auth/register', json={
            'email': 'not-an-email',
            'password': 'weak',
            'first_name': 'Test'
            # Missing last_name
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client, regular_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'User123!'
        })
        
        assert response.status_code == 200
        data = response.json
        assert 'access_token' in data
        assert 'user' in data
        assert 'expires_at' in data
        assert data['user']['email'] == 'user@test.com'
    
    def test_login_invalid_credentials(self, client, regular_user):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'WrongPassword!'
        })
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com'
            # Missing password
        })
        
        assert response.status_code == 400
    
    def test_get_current_user(self, client, auth_headers_user):
        """Test getting current user profile."""
        response = client.get('/api/auth/me', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json
        assert data['email'] == 'user@test.com'
        assert 'password' not in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting profile without authentication."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_update_profile(self, client, auth_headers_user):
        """Test updating user profile."""
        response = client.put('/api/auth/me', 
            headers=auth_headers_user,
            json={
                'first_name': 'Updated',
                'last_name': 'Name',
                'phone_number': '+9999999999'
            }
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['user']['first_name'] == 'Updated'
        assert data['user']['last_name'] == 'Name'
    
    def test_change_password(self, client, auth_headers_user):
        """Test changing password."""
        response = client.post('/api/auth/change-password',
            headers=auth_headers_user,
            json={
                'current_password': 'User123!',
                'new_password': 'NewPassword123!'
            }
        )
        
        assert response.status_code == 200
        
        # Verify can login with new password
        login_response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'NewPassword123!'
        })
        assert login_response.status_code == 200
    
    def test_change_password_wrong_current(self, client, auth_headers_user):
        """Test changing password with wrong current password."""
        response = client.post('/api/auth/change-password',
            headers=auth_headers_user,
            json={
                'current_password': 'WrongPassword!',
                'new_password': 'NewPassword123!'
            }
        )
        
        assert response.status_code == 400
        assert 'incorrect' in response.json['error'].lower()
    
    def test_logout(self, client, auth_headers_user):
        """Test logout."""
        response = client.post('/api/auth/logout', headers=auth_headers_user)
        
        assert response.status_code == 200
        assert 'Logout successful' in response.json['message']
