"""Menu service for business logic."""
from datetime import date
from app import db
from app.models import Menu, MenuItem, Restaurant


class MenuService:
    """Service for menu operations."""
    
    @staticmethod
    def get_available_menus(target_date=None):
        """Get menus available for a specific date."""
        if target_date is None:
            target_date = date.today()
        elif isinstance(target_date, str):
            from datetime import datetime
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        menus = Menu.query.filter(
            Menu.is_active == True,
            Menu.available_from <= target_date,
            Menu.available_until >= target_date
        ).join(Restaurant).filter(
            Restaurant.is_active == True
        ).all()
        
        return menus
    
    @staticmethod
    def get_menu_with_items(menu_id):
        """Get menu with all items."""
        menu = db.session.get(Menu, menu_id)
        if not menu:
            return None
        
        # Eager load items
        items = MenuItem.query.filter_by(menu_id=menu_id).order_by(
            MenuItem.display_order,
            MenuItem.name
        ).all()
        
        return menu, items
    
    @staticmethod
    def validate_menu_date_range(available_from, available_until, restaurant_id):
        """Validate menu date range."""
        if available_from > available_until:
            raise ValueError('Start date must be before end date')
        
        if available_from < date.today():
            raise ValueError('Menu availability cannot start in the past')
        
        # Check for overlapping menus from same restaurant
        overlapping = Menu.query.filter(
            Menu.restaurant_id == restaurant_id,
            Menu.is_active == True,
            Menu.available_from <= available_until,
            Menu.available_until >= available_from
        ).first()
        
        if overlapping:
            raise ValueError(f'Menu dates overlap with existing menu: {overlapping.name}')
        
        return True
