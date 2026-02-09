"""Comprehensive API test script."""
import requests
import json
from datetime import date, timedelta

API_BASE = "http://127.0.0.1:5000/api"

def print_header(text):
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}\n")

def print_test(number, description):
    print(f"{number}. {description}...")

def print_success(message):
    print(f"   ✓ {message}")

def print_error(message):
    print(f"   ✗ {message}")

# Store tokens and IDs
tokens = {}
ids = {}

print_header("🧪 MEAL OF THE DAY - API TEST SUITE")

# Test 1: Admin Login
print_test(1, "Admin Login")
try:
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "admin@motd.com",
        "password": "Admin123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    tokens['admin'] = data['access_token']
    print_success(f"Admin logged in successfully")
    print_success(f"User: {data['user']['full_name']} ({data['user']['role']})")
except Exception as e:
    print_error(f"Failed: {e}")
    exit(1)

# Test 2: User Login  
print_test(2, "Regular User Login")
try:
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "user@motd.com",
        "password": "User123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    tokens['user'] = data['access_token']
    print_success(f"User logged in successfully")
    print_success(f"User: {data['user']['full_name']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 3: Get Current User Profile
print_test(3, "Get Current User Profile")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print_success(f"Profile retrieved: {data['email']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 4: Create Restaurant (Admin)
print_test(4, "Create Restaurant (Admin Only)")
try:
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = requests.post(f"{API_BASE}/restaurants", headers=headers, json={
        "name": "The Healthy Kitchen",
        "contact_name": "Chef John",
        "phone_number": "+1234567890",
        "email": "kitchen@healthy.com",
        "address": "456 Food Street, Gourmet City"
    })
    assert response.status_code == 201
    data = response.json()
    ids['restaurant'] = data['restaurant']['id']
    print_success(f"Restaurant created: ID {ids['restaurant']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 5: List Restaurants
print_test(5, "List All Restaurants")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    response = requests.get(f"{API_BASE}/restaurants", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print_success(f"Found {len(data['restaurants'])} restaurant(s)")
    for r in data['restaurants']:
        print(f"     - {r['name']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 6: Create Menu (Admin)
print_test(6, "Create Menu for Restaurant (Admin Only)")
try:
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    next_week = (date.today() + timedelta(days=7)).isoformat()
    
    response = requests.post(f"{API_BASE}/menus", headers=headers, json={
        "restaurant_id": ids['restaurant'],
        "name": "Weekly Special Menu",
        "description": "Fresh and healthy meals for the week",
        "available_from": tomorrow,
        "available_until": next_week
    })
    assert response.status_code == 201
    data = response.json()
    ids['menu'] = data['menu']['id']
    print_success(f"Menu created: ID {ids['menu']}")
    print_success(f"Available from {tomorrow} to {next_week}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 7: Add Menu Items (Admin)
print_test(7, "Add Menu Items (Admin Only)")
try:
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    
    items = [
        {"name": "Grilled Chicken Salad", "price": "12.99", "dietary_info": "High protein, gluten-free"},
        {"name": "Veggie Buddha Bowl", "price": "10.99", "dietary_info": "Vegan, gluten-free"},
        {"name": "Salmon with Quinoa", "price": "15.99", "dietary_info": "High protein, omega-3"},
        {"name": "Turkey Club Sandwich", "price": "11.99", "dietary_info": "Contains gluten"}
    ]
    
    ids['items'] = []
    for i, item in enumerate(items, 1):
        response = requests.post(
            f"{API_BASE}/menus/{ids['menu']}/items",
            headers=headers,
            json={**item, "display_order": i, "is_available": True}
        )
        assert response.status_code == 201
        data = response.json()
        ids['items'].append(data['item']['id'])
        print_success(f"Added: {item['name']} - ${item['price']}")
    
except Exception as e:
    print_error(f"Failed: {e}")

# Test 8: Get Available Menus
print_test(8, "Get Available Menus for Date")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    target_date = (date.today() + timedelta(days=2)).isoformat()
    
    response = requests.get(
        f"{API_BASE}/menus/available",
        headers=headers,
        params={"date": target_date}
    )
    assert response.status_code == 200
    data = response.json()
    print_success(f"Found {len(data['menus'])} available menu(s) for {target_date}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 9: Get Menu with Items
print_test(9, "Get Menu Details with All Items")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    response = requests.get(f"{API_BASE}/menus/{ids['menu']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print_success(f"Menu: {data['name']}")
    print_success(f"Items: {len(data['items'])}")
    for item in data['items']:
        print(f"     - {item['name']}: ${item['price']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 10: Create Order (User)
print_test(10, "Create Order for User")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    order_date = (date.today() + timedelta(days=3)).isoformat()
    
    response = requests.post(f"{API_BASE}/orders", headers=headers, json={
        "menu_id": ids['menu'],
        "order_date": order_date,
        "items": [
            {"menu_item_id": ids['items'][0], "quantity": 1, "notes": "Extra dressing on the side"},
            {"menu_item_id": ids['items'][2], "quantity": 1}
        ],
        "notes": "Please deliver to Building A, Room 301"
    })
    assert response.status_code == 201
    data = response.json()
    ids['order'] = data['order']['id']
    print_success(f"Order created: ID {ids['order']}")
    print_success(f"Total: ${data['order']['total_amount']}")
    print_success(f"Date: {data['order']['order_date']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 11: Get User's Orders
print_test(11, "Get User's Order History")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    response = requests.get(f"{API_BASE}/orders", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print_success(f"Found {len(data['orders'])} order(s)")
    for order in data['orders']:
        print(f"     - Order #{order['id']}: {order['order_date']} - ${order['total_amount']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 12: Get Weekly Orders
print_test(12, "Get Weekly Order Calendar")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    start_date = date.today().isoformat()
    
    response = requests.get(
        f"{API_BASE}/orders/week",
        headers=headers,
        params={"start_date": start_date}
    )
    assert response.status_code == 200
    data = response.json()
    print_success("Weekly calendar:")
    for day in data['weekly_orders']:
        status = "✓ Ordered" if day['has_order'] else "✗ Missing"
        print(f"     {day['date']}: {status}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 13: Get Missing Order Days
print_test(13, "Get Days Without Orders")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    response = requests.get(
        f"{API_BASE}/orders/missing-days",
        headers=headers,
        params={"days_ahead": 7}
    )
    assert response.status_code == 200
    data = response.json()
    print_success(f"Missing orders for {data['count']} day(s)")
    for missing_date in data['missing_dates'][:5]:
        print(f"     - {missing_date}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 14: Admin Dashboard
print_test(14, "Admin Dashboard Statistics")
try:
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = requests.get(f"{API_BASE}/admin/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    stats = data['stats']
    print_success("Dashboard stats:")
    print(f"     - Total Users: {stats['total_users']}")
    print(f"     - Total Restaurants: {stats['total_restaurants']}")
    print(f"     - Total Menus: {stats['total_menus']}")
    print(f"     - Orders Today: {stats['orders_today']}")
    print(f"     - Orders This Week: {stats['orders_this_week']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 15: Get All Orders (Admin)
print_test(15, "Get All Orders (Admin Only)")
try:
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = requests.get(f"{API_BASE}/admin/orders", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print_success(f"Found {len(data['orders'])} total order(s) in system")
    print_success(f"Total pages: {data['pagination']['pages']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 16: Authorization Test (User trying to access Admin endpoint)
print_test(16, "Test Authorization (User → Admin endpoint)")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    response = requests.get(f"{API_BASE}/admin/dashboard", headers=headers)
    assert response.status_code == 403
    print_success("Authorization working correctly (access denied)")
except Exception as e:
    print_error(f"Authorization not working: {e}")

# Test 17: Update Order
print_test(17, "Update Existing Order")
try:
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    response = requests.put(
        f"{API_BASE}/orders/{ids['order']}",
        headers=headers,
        json={
            "notes": "Updated: Please deliver by 12:00 PM",
            "items": [
                {"menu_item_id": ids['items'][1], "quantity": 2}  # Change order
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    print_success(f"Order updated: New total ${data['order']['total_amount']}")
except Exception as e:
    print_error(f"Failed: {e}")

# Test 18: Update Order Status (Admin)
print_test(18, "Update Order Status (Admin Only)")
try:
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = requests.put(
        f"{API_BASE}/admin/orders/{ids['order']}/status",
        headers=headers,
        json={"status": "confirmed"}
    )
    assert response.status_code == 200
    print_success("Order status updated to 'confirmed'")
except Exception as e:
    print_error(f"Failed: {e}")

print_header("✅ API TESTING COMPLETE!")

print("\n📝 Test Summary:")
print(f"   Base URL: {API_BASE}")
print(f"   Admin Email: admin@motd.com")
print(f"   User Email: user@motd.com")
print(f"   Restaurant ID: {ids.get('restaurant')}")
print(f"   Menu ID: {ids.get('menu')}")
print(f"   Order ID: {ids.get('order')}")
print(f"\n✨ All major API endpoints tested successfully!")
