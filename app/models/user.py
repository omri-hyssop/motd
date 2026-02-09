"""User model."""
from datetime import datetime
from app import db, bcrypt


class User(db.Model):
    """User model for authentication and profile."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))  # For WhatsApp reminders
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    orders = db.relationship('Order', back_populates='user', lazy='dynamic')
    reminders = db.relationship('Reminder', back_populates='user', lazy='dynamic')
    sessions = db.relationship('Session', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, email, password, first_name, last_name, phone_number=None, role='user'):
        """Initialize user with hashed password."""
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.role = role

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of user."""
        return f'<User {self.email}>'
