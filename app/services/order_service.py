"""Order service for business logic."""
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Order, OrderItem, Menu, MenuItem, RestaurantAvailability
from app.utils.helpers import get_week_dates


class OrderService:
    """Service for order operations."""

    @staticmethod
    def _is_restaurant_available(restaurant_id, weekday):
        """Return True if restaurant is available on weekday (0=Mon..6=Sun)."""
        has_any = RestaurantAvailability.query.filter_by(restaurant_id=restaurant_id).first() is not None
        if not has_any:
            return False
        return (
            RestaurantAvailability.query.filter_by(
                restaurant_id=restaurant_id,
                weekday=weekday,
                is_available=True
            ).first()
            is not None
        )
    
    @staticmethod
    def create_order(user_id, menu_id, order_date, items_data, notes=None):
        """Create a new order with items."""
        if order_date.weekday() > 4:
            raise ValueError('Orders can only be placed Monday to Friday')

        # Validate menu exists and is available for the date
        menu = db.session.get(Menu, menu_id)
        if not menu:
            raise ValueError('Menu not found')
        
        if not menu.is_active:
            raise ValueError('Menu is not active')
        
        if not (menu.available_from <= order_date <= menu.available_until):
            raise ValueError('Menu is not available for the selected date')

        if not OrderService._is_restaurant_available(menu.restaurant_id, order_date.weekday()):
            raise ValueError('Restaurant is not available on the selected day')
        
        # Check if user already has an order for this date
        existing_order = Order.query.filter_by(
            user_id=user_id,
            order_date=order_date
        ).first()
        
        if existing_order:
            raise ValueError('You already have an order for this date')
        
        # Validate and calculate order items
        order_items = []
        total_amount = Decimal('0.00')
        
        for item_data in items_data:
            menu_item = db.session.get(MenuItem, item_data['menu_item_id'])
            if not menu_item:
                raise ValueError(f'Menu item {item_data["menu_item_id"]} not found')
            
            if menu_item.menu_id != menu_id:
                raise ValueError(f'Menu item {menu_item.id} does not belong to this menu')
            
            if not menu_item.is_available:
                raise ValueError(f'Menu item {menu_item.name} is not available')
            
            quantity = item_data['quantity']
            price = menu_item.price
            subtotal = price * quantity
            total_amount += subtotal
            
            order_items.append({
                'menu_item_id': menu_item.id,
                'quantity': quantity,
                'price': price,
                'notes': item_data.get('notes')
            })
        
        if not order_items:
            raise ValueError('Order must contain at least one item')
        
        # Create order
        order = Order(
            user_id=user_id,
            menu_id=menu_id,
            restaurant_id=menu.restaurant_id,
            order_date=order_date,
            total_amount=total_amount,
            notes=notes,
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order.id
        
        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return order

    @staticmethod
    def create_simple_order(user_id, restaurant_id, order_date, order_text, notes=None):
        """Create a freeform order tied to the restaurant's active menu."""
        if order_date.weekday() > 4:
            raise ValueError('Orders can only be placed Monday to Friday')

        if not OrderService._is_restaurant_available(restaurant_id, order_date.weekday()):
            raise ValueError('Restaurant is not available on the selected day')

        menu = Menu.query.filter(
            Menu.restaurant_id == restaurant_id,
            Menu.is_active.is_(True),
            Menu.available_from <= order_date,
            Menu.available_until >= order_date,
        ).first()
        if not menu:
            raise ValueError('Menu not found for this restaurant/date')

        existing_order = Order.query.filter_by(user_id=user_id, order_date=order_date).first()
        if existing_order:
            raise ValueError('You already have an order for this date')

        order = Order(
            user_id=user_id,
            menu_id=menu.id,
            restaurant_id=restaurant_id,
            order_date=order_date,
            total_amount=Decimal('0.00'),
            order_text=order_text,
            notes=notes,
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    @staticmethod
    def get_user_orders(user_id, status=None, date_from=None, date_to=None):
        """Get user's orders with optional filters."""
        query = Order.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if date_from:
            query = query.filter(Order.order_date >= date_from)
        
        if date_to:
            query = query.filter(Order.order_date <= date_to)
        
        return query.order_by(Order.order_date.desc()).all()
    
    @staticmethod
    def get_weekly_orders(user_id, start_date=None):
        """Get user's orders for a week."""
        if start_date is None:
            start_date = date.today()
        elif isinstance(start_date, str):
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        week_dates = get_week_dates(start_date, days=7)
        end_date = week_dates[-1]
        
        # Get orders for the week
        orders = Order.query.filter(
            Order.user_id == user_id,
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).all()
        
        # Create map of date -> order
        orders_by_date = {order.order_date: order for order in orders}
        
        # Build result with all dates
        result = []
        for target_date in week_dates:
            order = orders_by_date.get(target_date)
            result.append({
                'date': target_date,
                'has_order': order is not None,
                'order': order.to_dict(include_items=True) if order else None
            })
        
        return result
    
    @staticmethod
    def get_missing_order_days(user_id, days_ahead=7, start_date=None):
        """Get dates where user hasn't ordered yet."""
        if start_date is None:
            start_date = date.today()
        elif isinstance(start_date, str):
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        end_date = start_date + timedelta(days=days_ahead - 1)
        
        # Get existing orders
        existing_orders = Order.query.filter(
            Order.user_id == user_id,
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).all()
        
        ordered_dates = {order.order_date for order in existing_orders}
        
        # Find missing dates
        missing_dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date not in ordered_dates:
                missing_dates.append(current_date)
            current_date += timedelta(days=1)
        
        return missing_dates
    
    @staticmethod
    def update_order(order_id, user_id, items_data=None, notes=None):
        """Update an existing order."""
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            raise ValueError('Order not found')
        
        if order.status != 'pending':
            raise ValueError('Can only update pending orders')
        
        # Update notes if provided
        if notes is not None:
            order.notes = notes
        
        # Update items if provided
        if items_data:
            # Delete existing items
            OrderItem.query.filter_by(order_id=order_id).delete()
            
            # Recreate items
            total_amount = Decimal('0.00')
            for item_data in items_data:
                menu_item = db.session.get(MenuItem, item_data['menu_item_id'])
                if not menu_item:
                    raise ValueError(f'Menu item {item_data["menu_item_id"]} not found')
                
                if menu_item.menu_id != order.menu_id:
                    raise ValueError(f'Menu item does not belong to order menu')
                
                quantity = item_data['quantity']
                price = menu_item.price
                total_amount += price * quantity
                
                order_item = OrderItem(
                    order_id=order_id,
                    menu_item_id=menu_item.id,
                    quantity=quantity,
                    price=price,
                    notes=item_data.get('notes')
                )
                db.session.add(order_item)
            
            order.total_amount = total_amount
        
        db.session.commit()
        return order

    @staticmethod
    def update_simple_order(order_id, user_id, restaurant_id, order_text, notes=None):
        """Update an existing freeform order (pending only)."""
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            raise ValueError('Order not found')
        if order.status != 'pending':
            raise ValueError('Can only update pending orders')
        if order.order_date.weekday() > 4:
            raise ValueError('Orders can only be placed Monday to Friday')

        if not OrderService._is_restaurant_available(restaurant_id, order.order_date.weekday()):
            raise ValueError('Restaurant is not available on the selected day')

        menu = Menu.query.filter(
            Menu.restaurant_id == restaurant_id,
            Menu.is_active.is_(True),
            Menu.available_from <= order.order_date,
            Menu.available_until >= order.order_date,
        ).first()
        if not menu:
            raise ValueError('Menu not found for this restaurant/date')

        order.menu_id = menu.id
        order.restaurant_id = restaurant_id
        order.order_text = order_text
        if notes is not None:
            order.notes = notes

        # ensure no structured items remain
        OrderItem.query.filter_by(order_id=order.id).delete()
        order.total_amount = Decimal('0.00')

        db.session.commit()
        return order
    
    @staticmethod
    def cancel_order(order_id, user_id):
        """Cancel an order."""
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            raise ValueError('Order not found')
        
        if order.status in ['completed', 'cancelled']:
            raise ValueError('Cannot cancel completed or already cancelled orders')
        
        order.status = 'cancelled'
        db.session.commit()
        
        return order
    
    @staticmethod
    def update_order_status(order_id, status):
        """Update order status (admin only)."""
        order = db.session.get(Order, order_id)
        if not order:
            raise ValueError('Order not found')
        
        valid_statuses = ['pending', 'ordered', 'confirmed', 'sent_to_restaurant', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        
        order.status = status
        db.session.commit()
        
        return order
