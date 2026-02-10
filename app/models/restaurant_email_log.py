"""Tracking logs for restaurant order emails."""
from datetime import datetime
from app import db


class RestaurantOrderEmailLog(db.Model):
    """Record when order summary emails were sent (or logged) per restaurant/day."""
    __tablename__ = 'restaurant_order_email_logs'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False, index=True)
    order_date = db.Column(db.Date, nullable=False, index=True)
    sent_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    restaurant = db.relationship('Restaurant')
    sent_by_user = db.relationship('User')

    __table_args__ = (
        db.UniqueConstraint('restaurant_id', 'order_date', name='uq_restaurant_order_email_date'),
        db.Index('idx_email_logs_date_restaurant', 'order_date', 'restaurant_id'),
    )

