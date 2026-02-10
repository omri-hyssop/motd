"""Restaurant availability by weekday."""
from datetime import datetime
from app import db


class RestaurantAvailability(db.Model):
    """Availability for a restaurant on a given weekday (0=Mon ... 6=Sun)."""
    __tablename__ = 'restaurant_availability'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False, index=True)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Mon ... 6=Sun
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('restaurant_id', 'weekday', name='uq_restaurant_weekday'),
        db.Index('idx_weekday_available', 'weekday', 'is_available'),
    )

