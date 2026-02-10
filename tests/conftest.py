"""Pytest configuration and fixtures."""
import pytest
from datetime import date, timedelta
from app import create_app, db
from app.models import User, Restaurant, RestaurantAvailability, Menu, MenuItem, Order, OrderItem


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        # Clear all tables
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        
        yield db.session
        
        # Cleanup after test
        db.session.remove()


@pytest.fixture
def admin_user(db_session):
    """Create admin user."""
    user = User(
        email='admin@test.com',
        password='Admin123!',
        first_name='Admin',
        last_name='User',
        phone_number='+1234567890',
        role='admin'
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def regular_user(db_session):
    """Create regular user."""
    user = User(
        email='user@test.com',
        password='User123!',
        first_name='Test',
        last_name='User',
        phone_number='+9876543210',
        role='user'
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_token(client, admin_user):
    """Get admin JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'Admin123!'
    })
    return response.json['access_token']


@pytest.fixture
def user_token(client, regular_user):
    """Get regular user JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'user@test.com',
        'password': 'User123!'
    })
    return response.json['access_token']


@pytest.fixture
def restaurant(db_session):
    """Create test restaurant."""
    restaurant = Restaurant(
        name='Test Restaurant',
        contact_name='Chef Test',
        phone_number='+1234567890',
        email='chef@test.com',
        address='123 Test St'
    )
    db_session.add(restaurant)
    db_session.commit()
    # Default availability: Mon-Fri
    for w in range(5):
        db_session.add(RestaurantAvailability(restaurant_id=restaurant.id, weekday=w, is_available=True))
    db_session.commit()
    return restaurant


@pytest.fixture
def menu(db_session, restaurant):
    """Create test menu."""
    tomorrow = date.today() + timedelta(days=1)
    next_week = date.today() + timedelta(days=7)
    
    menu = Menu(
        restaurant_id=restaurant.id,
        name='Test Menu',
        description='Test menu description',
        available_from=tomorrow,
        available_until=next_week,
        is_active=True
    )
    db_session.add(menu)
    db_session.commit()
    return menu


@pytest.fixture
def menu_items(db_session, menu):
    """Create test menu items."""
    items = [
        MenuItem(
            menu_id=menu.id,
            name='Chicken Salad',
            description='Fresh chicken salad',
            price=12.99,
            dietary_info='High protein',
            is_available=True,
            display_order=1
        ),
        MenuItem(
            menu_id=menu.id,
            name='Veggie Bowl',
            description='Healthy veggie bowl',
            price=10.99,
            dietary_info='Vegan',
            is_available=True,
            display_order=2
        ),
        MenuItem(
            menu_id=menu.id,
            name='Fish Tacos',
            description='Grilled fish tacos',
            price=13.99,
            dietary_info='Pescatarian',
            is_available=True,
            display_order=3
        )
    ]
    
    for item in items:
        db_session.add(item)
    db_session.commit()
    
    return items


@pytest.fixture
def order(db_session, regular_user, menu, menu_items):
    """Create test order."""
    order_date = date.today() + timedelta(days=2)
    
    order = Order(
        user_id=regular_user.id,
        menu_id=menu.id,
        restaurant_id=menu.restaurant_id,
        order_date=order_date,
        total_amount=23.98,
        status='pending'
    )
    db_session.add(order)
    db_session.flush()
    
    # Add order items
    order_item1 = OrderItem(
        order_id=order.id,
        menu_item_id=menu_items[0].id,
        quantity=1,
        price=menu_items[0].price
    )
    order_item2 = OrderItem(
        order_id=order.id,
        menu_item_id=menu_items[1].id,
        quantity=1,
        price=menu_items[1].price
    )
    
    db_session.add(order_item1)
    db_session.add(order_item2)
    db_session.commit()
    
    return order


@pytest.fixture
def auth_headers_admin(admin_token):
    """Get authorization headers for admin."""
    return {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def auth_headers_user(user_token):
    """Get authorization headers for regular user."""
    return {
        'Authorization': f'Bearer {user_token}',
        'Content-Type': 'application/json'
    }
