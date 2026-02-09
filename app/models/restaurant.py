"""Restaurant model."""
from datetime import datetime
from app import db


class Restaurant(db.Model):
    """Restaurant model."""
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(200))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    menus = db.relationship('Menu', back_populates='restaurant', lazy='dynamic')
    orders = db.relationship('Order', back_populates='restaurant', lazy='dynamic')
    order_summaries = db.relationship('RestaurantOrderSummary', back_populates='restaurant', lazy='dynamic')

    def to_dict(self):
        """Convert restaurant to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'contact_name': self.contact_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of restaurant."""
        return f'<Restaurant {self.name}>'
