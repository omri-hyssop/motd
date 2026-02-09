"""Integration tests for restaurant and menu endpoints."""
import pytest
from datetime import date, timedelta


class TestRestaurantEndpoints:
    """Test restaurant API endpoints."""
    
    def test_list_restaurants(self, client, auth_headers_user, restaurant):
        """Test listing restaurants."""
        response = client.get('/api/restaurants', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json
        assert 'restaurants' in data
        assert len(data['restaurants']) >= 1
    
    def test_create_restaurant_admin(self, client, auth_headers_admin):
        """Test admin can create restaurant."""
        response = client.post('/api/restaurants',
            headers=auth_headers_admin,
            json={
                'name': 'New Restaurant',
                'contact_name': 'Chef John',
                'email': 'chef@new.com',
                'phone_number': '+1234567890',
                'address': '123 Main St'
            }
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['restaurant']['name'] == 'New Restaurant'
    
    def test_create_restaurant_unauthorized(self, client, auth_headers_user):
        """Test regular user cannot create restaurant."""
        response = client.post('/api/restaurants',
            headers=auth_headers_user,
            json={'name': 'Test'}
        )
        
        assert response.status_code == 403
    
    def test_get_restaurant(self, client, auth_headers_user, restaurant):
        """Test getting restaurant details."""
        response = client.get(f'/api/restaurants/{restaurant.id}',
            headers=auth_headers_user
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == restaurant.id
        assert data['name'] == restaurant.name
    
    def test_update_restaurant(self, client, auth_headers_admin, restaurant):
        """Test updating restaurant."""
        response = client.put(f'/api/restaurants/{restaurant.id}',
            headers=auth_headers_admin,
            json={'name': 'Updated Restaurant Name'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['restaurant']['name'] == 'Updated Restaurant Name'
    
    def test_deactivate_restaurant(self, client, auth_headers_admin, restaurant):
        """Test deactivating restaurant."""
        response = client.delete(f'/api/restaurants/{restaurant.id}',
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200


class TestMenuEndpoints:
    """Test menu API endpoints."""
    
    def test_list_menus(self, client, auth_headers_user, menu):
        """Test listing menus."""
        response = client.get('/api/menus', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json
        assert 'menus' in data
        assert len(data['menus']) >= 1
    
    def test_get_available_menus(self, client, auth_headers_user, menu):
        """Test getting available menus for date."""
        target_date = (date.today() + timedelta(days=2)).isoformat()
        
        response = client.get(f'/api/menus/available?date={target_date}',
            headers=auth_headers_user
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'menus' in data
        assert len(data['menus']) >= 1
    
    def test_create_menu_admin(self, client, auth_headers_admin, restaurant):
        """Test admin can create menu."""
        tomorrow = (date.today() + timedelta(days=10)).isoformat()
        next_week = (date.today() + timedelta(days=15)).isoformat()
        
        response = client.post('/api/menus',
            headers=auth_headers_admin,
            json={
                'restaurant_id': restaurant.id,
                'name': 'New Menu',
                'description': 'Test menu',
                'available_from': tomorrow,
                'available_until': next_week
            }
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['menu']['name'] == 'New Menu'
    
    def test_create_menu_unauthorized(self, client, auth_headers_user, restaurant):
        """Test regular user cannot create menu."""
        response = client.post('/api/menus',
            headers=auth_headers_user,
            json={'restaurant_id': restaurant.id, 'name': 'Test'}
        )
        
        assert response.status_code == 403
    
    def test_get_menu_with_items(self, client, auth_headers_user, menu, menu_items):
        """Test getting menu with items."""
        response = client.get(f'/api/menus/{menu.id}', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == menu.id
        assert 'items' in data
        assert len(data['items']) == 3
    
    def test_add_menu_item(self, client, auth_headers_admin, menu):
        """Test admin can add menu item."""
        response = client.post(f'/api/menus/{menu.id}/items',
            headers=auth_headers_admin,
            json={
                'name': 'New Item',
                'description': 'Test item',
                'price': '14.99',
                'dietary_info': 'Test',
                'is_available': True,
                'display_order': 4
            }
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['item']['name'] == 'New Item'
        assert float(data['item']['price']) == 14.99
    
    def test_update_menu_item(self, client, auth_headers_admin, menu_items):
        """Test updating menu item."""
        response = client.put(f'/api/menus/items/{menu_items[0].id}',
            headers=auth_headers_admin,
            json={
                'name': 'Updated Item Name',
                'price': '15.99'
            }
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['item']['name'] == 'Updated Item Name'
    
    def test_delete_menu_item(self, client, auth_headers_admin, menu_items):
        """Test deleting menu item."""
        response = client.delete(f'/api/menus/items/{menu_items[0].id}',
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
