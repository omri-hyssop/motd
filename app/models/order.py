"""Order and OrderItem models."""
from datetime import datetime
from app import db


class Order(db.Model):
    """Order model."""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)  # The date the meal is for
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending/confirmed/sent_to_restaurant/completed/cancelled
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    order_text = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    menu = db.relationship('Menu', back_populates='orders')
    restaurant = db.relationship('Restaurant', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', lazy='dynamic', cascade='all, delete-orphan')

    # Constraints and Indexes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'order_date', name='uq_user_order_date'),
        db.Index('idx_user_order_date', 'user_id', 'order_date'),
        db.Index('idx_order_date_status', 'order_date', 'status'),
    )

    def to_dict(self, include_items=False):
        """Convert order to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'menu_id': self.menu_id,
            'menu_name': self.menu.name if self.menu else None,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'status': self.status,
            'total_amount': float(self.total_amount) if self.total_amount else 0.0,
            'order_text': self.order_text,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data

    def __repr__(self):
        """String representation of order."""
        return f'<Order {self.id} - User {self.user_id} - {self.order_date}>'


class OrderItem(db.Model):
    """Order item model."""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Snapshot of price at order time
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    order = db.relationship('Order', back_populates='items')
    menu_item = db.relationship('MenuItem', back_populates='order_items')

    def to_dict(self):
        """Convert order item to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name if self.menu_item else None,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else 0.0,
            'subtotal': float(self.price * self.quantity) if self.price else 0.0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        """String representation of order item."""
        return f'<OrderItem {self.id} - Order {self.order_id}>'
