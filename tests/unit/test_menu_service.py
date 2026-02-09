"""Unit tests for menu service."""
import pytest
from datetime import date, timedelta
from app.services.menu_service import MenuService


class TestMenuService:
    """Test menu service."""
    
    def test_get_available_menus(self, app, db_session, menu):
        """Test getting available menus for a date."""
        with app.app_context():
            target_date = date.today() + timedelta(days=2)
            menus = MenuService.get_available_menus(target_date)
            
            assert len(menus) == 1
            assert menus[0].id == menu.id
    
    def test_get_available_menus_no_results(self, app, db_session, menu):
        """Test getting available menus when none match."""
        with app.app_context():
            # Try far future date
            far_future = date.today() + timedelta(days=365)
            menus = MenuService.get_available_menus(far_future)
            
            assert len(menus) == 0
    
    def test_get_menu_with_items(self, app, db_session, menu, menu_items):
        """Test getting menu with items."""
        with app.app_context():
            result = MenuService.get_menu_with_items(menu.id)
            
            assert result is not None
            menu_obj, items = result
            assert menu_obj.id == menu.id
            assert len(items) == 3
            # Check items are sorted by display_order
            assert items[0].display_order <= items[1].display_order
    
    def test_get_menu_with_items_not_found(self, app, db_session):
        """Test getting non-existent menu."""
        with app.app_context():
            result = MenuService.get_menu_with_items(9999)
            
            assert result is None
    
    def test_validate_menu_date_range_success(self, app, db_session, restaurant):
        """Test validating valid date range."""
        with app.app_context():
            available_from = date.today() + timedelta(days=10)
            available_until = date.today() + timedelta(days=15)
            
            result = MenuService.validate_menu_date_range(
                available_from,
                available_until,
                restaurant.id
            )
            
            assert result is True
    
    def test_validate_menu_date_range_reversed(self, app, db_session, restaurant):
        """Test validating invalid date range (end before start)."""
        with app.app_context():
            available_from = date.today() + timedelta(days=15)
            available_until = date.today() + timedelta(days=10)
            
            with pytest.raises(ValueError, match='Start date must be before end date'):
                MenuService.validate_menu_date_range(
                    available_from,
                    available_until,
                    restaurant.id
                )
    
    def test_validate_menu_date_range_past(self, app, db_session, restaurant):
        """Test validating date range in the past."""
        with app.app_context():
            available_from = date.today() - timedelta(days=5)
            available_until = date.today() + timedelta(days=5)
            
            with pytest.raises(ValueError, match='cannot start in the past'):
                MenuService.validate_menu_date_range(
                    available_from,
                    available_until,
                    restaurant.id
                )
    
    def test_validate_menu_date_range_overlapping(self, app, db_session, menu, restaurant):
        """Test validating overlapping date ranges."""
        with app.app_context():
            # Try to create menu with overlapping dates
            available_from = date.today() + timedelta(days=2)
            available_until = date.today() + timedelta(days=5)
            
            with pytest.raises(ValueError, match='overlap'):
                MenuService.validate_menu_date_range(
                    available_from,
                    available_until,
                    restaurant.id
                )
