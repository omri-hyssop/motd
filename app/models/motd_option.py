"""Meal of the day (MOTD) options per restaurant and weekday."""
from datetime import datetime
from app import db


class MotdOption(db.Model):
    """A quick MOTD option for a restaurant on a specific weekday."""
    __tablename__ = 'motd_options'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False, index=True)
    # weekday: 0=Mon ... 6=Sun. Admin UI uses Mon-Fri.
    weekday = db.Column(db.Integer, nullable=False, index=True)
    # legacy column (kept for backwards compatibility / existing rows)
    motd_date = db.Column(db.Date, nullable=True, index=True)
    option_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    restaurant = db.relationship('Restaurant')

    __table_args__ = (
        db.UniqueConstraint('restaurant_id', 'weekday', name='uq_restaurant_motd_weekday'),
        db.Index('idx_motd_weekday_restaurant', 'weekday', 'restaurant_id'),
    )
