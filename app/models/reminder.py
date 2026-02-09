"""Reminder and related models."""
from datetime import datetime
from app import db


class Reminder(db.Model):
    """Reminder model for tracking sent reminders."""
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    reminder_type = db.Column(db.String(20), nullable=False)  # 'whatsapp' or 'email'
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending/sent/failed/delivered
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    failure_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='reminders')

    # Indexes
    __table_args__ = (
        db.Index('idx_reminder_user_date', 'user_id', 'order_date'),
        db.Index('idx_reminder_status_created', 'status', 'created_at'),
    )

    def to_dict(self):
        """Convert reminder to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'reminder_type': self.reminder_type,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'failure_reason': self.failure_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        """String representation of reminder."""
        return f'<Reminder {self.id} - User {self.user_id} - {self.order_date}>'


class ReminderSchedule(db.Model):
    """Reminder schedule configuration."""
    __tablename__ = 'reminder_schedules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    days_ahead = db.Column(db.Integer, nullable=False)  # How many days ahead to remind
    reminder_time = db.Column(db.Time, nullable=False)  # Time to send reminder
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert reminder schedule to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'days_ahead': self.days_ahead,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of reminder schedule."""
        return f'<ReminderSchedule {self.name}>'


class RestaurantOrderSummary(db.Model):
    """Restaurant order summary tracking."""
    __tablename__ = 'restaurant_order_summaries'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    sent_at = db.Column(db.DateTime)
    email_status = db.Column(db.String(20))  # sent/failed
    summary_data = db.Column(db.JSON)  # Aggregated order data
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    restaurant = db.relationship('Restaurant', back_populates='order_summaries')

    # Indexes
    __table_args__ = (
        db.Index('idx_restaurant_summary_date', 'restaurant_id', 'order_date'),
    )

    def to_dict(self):
        """Convert restaurant order summary to dictionary."""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'email_status': self.email_status,
            'summary_data': self.summary_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        """String representation of restaurant order summary."""
        return f'<RestaurantOrderSummary {self.id} - Restaurant {self.restaurant_id} - {self.order_date}>'


class Session(db.Model):
    """User session model for JWT token management."""
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='sessions')

    def is_expired(self):
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        """String representation of session."""
        return f'<Session {self.id} - User {self.user_id}>'
