"""Create test admin user."""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@motd.com').first()
    if not admin:
        admin = User(
            email='admin@motd.com',
            password='Admin123!',
            first_name='Admin',
            last_name='User',
            phone_number='+1234567890',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✓ Admin user created: admin@motd.com / Admin123!")
    else:
        print(f"✓ Admin user already exists: admin@motd.com")
    
    # Create test user
    user = User.query.filter_by(email='user@motd.com').first()
    if not user:
        user = User(
            email='user@motd.com',
            password='User123!',
            first_name='Test',
            last_name='User',
            phone_number='+19876543210',
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        print(f"✓ Test user created: user@motd.com / User123!")
    else:
        print(f"✓ Test user already exists: user@motd.com")
