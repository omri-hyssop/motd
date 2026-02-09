"""Integration tests for order endpoints."""
import pytest
from datetime import date, timedelta


class TestOrderEndpoints:
    """Test order API endpoints."""
    
    def test_create_order_success(self, client, auth_headers_user, menu, menu_items):
        """Test successful order creation."""
        order_date = (date.today() + timedelta(days=2)).isoformat()
        
        response = client.post('/api/orders',
            headers=auth_headers_user,
            json={
                'menu_id': menu.id,
                'order_date': order_date,
                'items': [
                    {'menu_item_id': menu_items[0].id, 'quantity': 1},
                    {'menu_item_id': menu_items[1].id, 'quantity': 2}
                ],
                'notes': 'Test order'
            }
        )
        
        assert response.status_code == 201
        data = response.json
        assert 'order' in data
        assert data['order']['order_date'] == order_date
        assert float(data['order']['total_amount']) == 34.97  # 12.99 + (10.99 * 2)
    
    def test_create_order_unauthorized(self, client, menu, menu_items):
        """Test creating order without authentication."""
        order_date = (date.today() + timedelta(days=2)).isoformat()
        
        response = client.post('/api/orders', json={
            'menu_id': menu.id,
            'order_date': order_date,
            'items': [{'menu_item_id': menu_items[0].id, 'quantity': 1}]
        })
        
        assert response.status_code == 401
    
    def test_create_order_duplicate_date(self, client, auth_headers_user, order, menu, menu_items):
        """Test creating duplicate order for same date."""
        response = client.post('/api/orders',
            headers=auth_headers_user,
            json={
                'menu_id': menu.id,
                'order_date': order.order_date.isoformat(),
                'items': [{'menu_item_id': menu_items[0].id, 'quantity': 1}]
            }
        )
        
        assert response.status_code == 400
        assert 'already have an order' in response.json['error']
    
    def test_get_user_orders(self, client, auth_headers_user, order):
        """Test getting user's orders."""
        response = client.get('/api/orders', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json
        assert 'orders' in data
        assert len(data['orders']) == 1
        assert data['orders'][0]['id'] == order.id
    
    def test_get_order_detail(self, client, auth_headers_user, order):
        """Test getting order details."""
        response = client.get(f'/api/orders/{order.id}', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == order.id
        assert 'items' in data
        assert len(data['items']) == 2
    
    def test_get_order_not_found(self, client, auth_headers_user):
        """Test getting non-existent order."""
        response = client.get('/api/orders/9999', headers=auth_headers_user)
        
        assert response.status_code == 404
    
    def test_update_order(self, client, auth_headers_user, order, menu_items):
        """Test updating an order."""
        response = client.put(f'/api/orders/{order.id}',
            headers=auth_headers_user,
            json={
                'notes': 'Updated notes',
                'items': [{'menu_item_id': menu_items[2].id, 'quantity': 1}]
            }
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['order']['notes'] == 'Updated notes'
        assert float(data['order']['total_amount']) == 13.99
    
    def test_cancel_order(self, client, auth_headers_user, order):
        """Test cancelling an order."""
        response = client.delete(f'/api/orders/{order.id}', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json
        assert data['order']['status'] == 'cancelled'
    
    def test_get_weekly_orders(self, client, auth_headers_user, order):
        """Test getting weekly orders."""
        start_date = date.today().isoformat()
        
        response = client.get(f'/api/orders/week?start_date={start_date}',
            headers=auth_headers_user
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'weekly_orders' in data
        assert len(data['weekly_orders']) == 7
        
        # Check structure
        for day in data['weekly_orders']:
            assert 'date' in day
            assert 'has_order' in day
            assert 'order' in day
    
    def test_get_missing_days(self, client, auth_headers_user, order):
        """Test getting missing order days."""
        response = client.get('/api/orders/missing-days?days_ahead=7',
            headers=auth_headers_user
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'missing_dates' in data
        assert 'count' in data
        assert data['count'] == 6  # 7 days - 1 with order
        assert order.order_date.isoformat() not in data['missing_dates']


class TestAdminOrderEndpoints:
    """Test admin order endpoints."""
    
    def test_get_all_orders_admin(self, client, auth_headers_admin, order):
        """Test admin can get all orders."""
        response = client.get('/api/admin/orders', headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json
        assert 'orders' in data
        assert 'pagination' in data
        assert len(data['orders']) >= 1
    
    def test_get_all_orders_unauthorized(self, client, auth_headers_user):
        """Test regular user cannot access admin endpoint."""
        response = client.get('/api/admin/orders', headers=auth_headers_user)
        
        assert response.status_code == 403
    
    def test_update_order_status(self, client, auth_headers_admin, order):
        """Test admin can update order status."""
        response = client.put(f'/api/admin/orders/{order.id}/status',
            headers=auth_headers_admin,
            json={'status': 'confirmed'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['order']['status'] == 'confirmed'
    
    def test_get_dashboard_stats(self, client, auth_headers_admin, order):
        """Test admin dashboard statistics."""
        response = client.get('/api/admin/dashboard', headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json
        assert 'stats' in data
        assert 'total_users' in data['stats']
        assert 'total_restaurants' in data['stats']
        assert 'orders_this_week' in data['stats']
    
    def test_get_users_without_orders(self, client, auth_headers_admin):
        """Test getting users without orders."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        response = client.get(f'/api/admin/users-without-orders?date={tomorrow}',
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'users' in data
        assert 'count' in data
        assert isinstance(data['users'], list)
