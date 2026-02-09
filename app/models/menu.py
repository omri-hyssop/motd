"""Menu and MenuItem models."""
from datetime import datetime
from app import db


class Menu(db.Model):
    """Menu model."""
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    available_from = db.Column(db.Date, nullable=False)
    available_until = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    restaurant = db.relationship('Restaurant', back_populates='menus')
    items = db.relationship('MenuItem', back_populates='menu', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', back_populates='menu', lazy='dynamic')

    # Indexes
    __table_args__ = (
        db.Index('idx_menu_restaurant_dates', 'restaurant_id', 'available_from', 'available_until'),
    )

    def to_dict(self, include_items=False):
        """Convert menu to dictionary."""
        data = {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'name': self.name,
            'description': self.description,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'available_until': self.available_until.isoformat() if self.available_until else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data

    def __repr__(self):
        """String representation of menu."""
        return f'<Menu {self.name}>'


class MenuItem(db.Model):
    """Menu item model."""
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    dietary_info = db.Column(db.String(200))  # e.g., "vegetarian, gluten-free"
    image_url = db.Column(db.String(500))
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    menu = db.relationship('Menu', back_populates='items')
    order_items = db.relationship('OrderItem', back_populates='menu_item', lazy='dynamic')

    def to_dict(self):
        """Convert menu item to dictionary."""
        return {
            'id': self.id,
            'menu_id': self.menu_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'dietary_info': self.dietary_info,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of menu item."""
        return f'<MenuItem {self.name}>'
