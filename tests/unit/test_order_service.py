"""Unit tests for order service."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from app.services.order_service import OrderService
from app.models import Order


class TestOrderService:
    """Test order service."""
    
    def test_create_order_success(self, app, db_session, regular_user, menu, menu_items):
        """Test successful order creation."""
        with app.app_context():
            order_date = date.today() + timedelta(days=2)
            
            order = OrderService.create_order(
                user_id=regular_user.id,
                menu_id=menu.id,
                order_date=order_date,
                items_data=[
                    {'menu_item_id': menu_items[0].id, 'quantity': 2, 'notes': 'Extra sauce'},
                    {'menu_item_id': menu_items[1].id, 'quantity': 1}
                ],
                notes='Deliver to office'
            )
            
            assert order.id is not None
            assert order.user_id == regular_user.id
            assert order.menu_id == menu.id
            assert order.order_date == order_date
            assert order.status == 'pending'
            assert order.total_amount == Decimal('36.97')  # (12.99 * 2) + 10.99
            assert order.notes == 'Deliver to office'
            assert len(list(order.items)) == 2
    
    def test_create_order_duplicate_date(self, app, db_session, regular_user, menu, menu_items, order):
        """Test creating duplicate order for same date fails."""
        with app.app_context():
            with pytest.raises(ValueError, match='already have an order for this date'):
                OrderService.create_order(
                    user_id=regular_user.id,
                    menu_id=menu.id,
                    order_date=order.order_date,  # Same date as existing order
                    items_data=[
                        {'menu_item_id': menu_items[0].id, 'quantity': 1}
                    ]
                )
    
    def test_create_order_invalid_menu(self, app, db_session, regular_user):
        """Test creating order with invalid menu fails."""
        with app.app_context():
            with pytest.raises(ValueError, match='Menu not found'):
                OrderService.create_order(
                    user_id=regular_user.id,
                    menu_id=9999,  # Non-existent menu
                    order_date=date.today() + timedelta(days=2),
                    items_data=[]
                )
    
    def test_create_order_date_outside_range(self, app, db_session, regular_user, menu, menu_items):
        """Test creating order for date outside menu availability."""
        with app.app_context():
            # Try to order for a date way in the future
            far_future = date.today() + timedelta(days=365)
            
            with pytest.raises(ValueError, match='Menu is not available'):
                OrderService.create_order(
                    user_id=regular_user.id,
                    menu_id=menu.id,
                    order_date=far_future,
                    items_data=[
                        {'menu_item_id': menu_items[0].id, 'quantity': 1}
                    ]
                )
    
    def test_create_order_no_items(self, app, db_session, regular_user, menu):
        """Test creating order with no items fails."""
        with app.app_context():
            order_date = date.today() + timedelta(days=2)
            
            with pytest.raises(ValueError, match='must contain at least one item'):
                OrderService.create_order(
                    user_id=regular_user.id,
                    menu_id=menu.id,
                    order_date=order_date,
                    items_data=[]
                )
    
    def test_get_user_orders(self, app, db_session, regular_user, order):
        """Test getting user's orders."""
        with app.app_context():
            orders = OrderService.get_user_orders(regular_user.id)
            
            assert len(orders) == 1
            assert orders[0].id == order.id
            assert orders[0].user_id == regular_user.id
    
    def test_get_user_orders_filtered_by_status(self, app, db_session, regular_user, order):
        """Test getting user's orders filtered by status."""
        with app.app_context():
            # Get pending orders
            pending_orders = OrderService.get_user_orders(regular_user.id, status='pending')
            assert len(pending_orders) == 1
            
            # Get confirmed orders (should be empty)
            confirmed_orders = OrderService.get_user_orders(regular_user.id, status='confirmed')
            assert len(confirmed_orders) == 0
    
    def test_get_weekly_orders(self, app, db_session, regular_user, order):
        """Test getting weekly orders."""
        with app.app_context():
            start_date = date.today()
            weekly_data = OrderService.get_weekly_orders(regular_user.id, start_date)
            
            assert len(weekly_data) == 7
            
            # Check structure
            for day in weekly_data:
                assert 'date' in day
                assert 'has_order' in day
                assert 'order' in day
                
                if day['has_order']:
                    assert day['order'] is not None
                else:
                    assert day['order'] is None
    
    def test_get_missing_order_days(self, app, db_session, regular_user, order):
        """Test getting missing order days."""
        with app.app_context():
            start_date = date.today()
            missing_dates = OrderService.get_missing_order_days(
                regular_user.id,
                days_ahead=7,
                start_date=start_date
            )
            
            # Should have 6 missing days (7 total - 1 with order)
            assert len(missing_dates) == 6
            
            # Order date should not be in missing dates
            assert order.order_date not in missing_dates
    
    def test_update_order(self, app, db_session, regular_user, order, menu_items):
        """Test updating an order."""
        with app.app_context():
            updated_order = OrderService.update_order(
                order_id=order.id,
                user_id=regular_user.id,
                items_data=[
                    {'menu_item_id': menu_items[2].id, 'quantity': 1}  # Fish Tacos
                ],
                notes='Updated notes'
            )
            
            assert updated_order.notes == 'Updated notes'
            assert updated_order.total_amount == Decimal('13.99')
            assert len(list(updated_order.items)) == 1
    
    def test_update_order_not_found(self, app, db_session, regular_user):
        """Test updating non-existent order."""
        with app.app_context():
            with pytest.raises(ValueError, match='Order not found'):
                OrderService.update_order(
                    order_id=9999,
                    user_id=regular_user.id,
                    notes='Updated'
                )
    
    def test_cancel_order(self, app, db_session, regular_user, order):
        """Test cancelling an order."""
        with app.app_context():
            cancelled_order = OrderService.cancel_order(order.id, regular_user.id)
            
            assert cancelled_order.status == 'cancelled'
    
    def test_cancel_completed_order(self, app, db_session, regular_user, order):
        """Test cancelling completed order fails."""
        with app.app_context():
            order.status = 'completed'
            db_session.commit()
            
            with pytest.raises(ValueError, match='Cannot cancel'):
                OrderService.cancel_order(order.id, regular_user.id)
    
    def test_update_order_status(self, app, db_session, order):
        """Test updating order status (admin function)."""
        with app.app_context():
            updated_order = OrderService.update_order_status(order.id, 'confirmed')
            
            assert updated_order.status == 'confirmed'
    
    def test_update_order_status_invalid(self, app, db_session, order):
        """Test updating order with invalid status fails."""
        with app.app_context():
            with pytest.raises(ValueError, match='Invalid status'):
                OrderService.update_order_status(order.id, 'invalid_status')
