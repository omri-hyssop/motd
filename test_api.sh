#!/bin/bash

API_URL="http://localhost:5000/api"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Testing Meal of the Day API"
echo "==============================="
echo ""

# Test 1: Login as admin
echo "1️⃣  Testing Admin Login..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@motd.com",
    "password": "Admin123!"
  }')

echo "$LOGIN_RESPONSE" | grep -q "access_token"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Admin login successful${NC}"
  ADMIN_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")
  echo "  Token: ${ADMIN_TOKEN:0:20}..."
else
  echo -e "${RED}✗ Admin login failed${NC}"
  echo "$LOGIN_RESPONSE"
  exit 1
fi
echo ""

# Test 2: Get current user
echo "2️⃣  Testing Get Current User (Admin)..."
PROFILE=$(curl -s "${API_URL}/auth/me" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "$PROFILE" | grep -q "admin@motd.com"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Profile retrieved${NC}"
  echo "$PROFILE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"  Name: {d['first_name']} {d['last_name']}\n  Role: {d['role']}\n  Email: {d['email']}\")"
else
  echo -e "${RED}✗ Failed to get profile${NC}"
fi
echo ""

# Test 3: Create a restaurant (admin only)
echo "3️⃣  Testing Create Restaurant (Admin)..."
RESTAURANT=$(curl -s -X POST "${API_URL}/restaurants" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Test Restaurant",
    "contact_name": "John Doe",
    "phone_number": "+1234567890",
    "email": "restaurant@test.com",
    "address": "123 Main St"
  }')

echo "$RESTAURANT" | grep -q "Restaurant created successfully"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Restaurant created${NC}"
  RESTAURANT_ID=$(echo "$RESTAURANT" | python3 -c "import sys, json; print(json.load(sys.stdin)['restaurant']['id'])")
  echo "  Restaurant ID: $RESTAURANT_ID"
else
  echo -e "${RED}✗ Failed to create restaurant${NC}"
  echo "$RESTAURANT"
fi
echo ""

# Test 4: List restaurants
echo "4️⃣  Testing List Restaurants..."
RESTAURANTS=$(curl -s "${API_URL}/restaurants" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "$RESTAURANTS" | grep -q "restaurants"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Restaurants listed${NC}"
  COUNT=$(echo "$RESTAURANTS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['restaurants']))")
  echo "  Total restaurants: $COUNT"
else
  echo -e "${RED}✗ Failed to list restaurants${NC}"
fi
echo ""

# Test 5: Create a menu (admin only)
echo "5️⃣  Testing Create Menu (Admin)..."
MENU=$(curl -s -X POST "${API_URL}/menus" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{
    \"restaurant_id\": $RESTAURANT_ID,
    \"name\": \"Weekly Lunch Menu\",
    \"description\": \"Delicious meals for the week\",
    \"available_from\": \"2026-02-10\",
    \"available_until\": \"2026-02-14\"
  }")

echo "$MENU" | grep -q "Menu created successfully"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Menu created${NC}"
  MENU_ID=$(echo "$MENU" | python3 -c "import sys, json; print(json.load(sys.stdin)['menu']['id'])")
  echo "  Menu ID: $MENU_ID"
else
  echo -e "${RED}✗ Failed to create menu${NC}"
  echo "$MENU"
fi
echo ""

# Test 6: Add menu items (admin only)
echo "6️⃣  Testing Add Menu Items (Admin)..."
ITEM1=$(curl -s -X POST "${API_URL}/menus/${MENU_ID}/items" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Grilled Chicken Sandwich",
    "description": "Juicy grilled chicken with lettuce and tomato",
    "price": "12.99",
    "dietary_info": "Contains gluten",
    "is_available": true,
    "display_order": 1
  }')

echo "$ITEM1" | grep -q "Menu item created successfully"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Menu item 1 created${NC}"
  ITEM1_ID=$(echo "$ITEM1" | python3 -c "import sys, json; print(json.load(sys.stdin)['item']['id'])")
  echo "  Item: Grilled Chicken Sandwich - \$12.99"
else
  echo -e "${RED}✗ Failed to create menu item 1${NC}"
fi

ITEM2=$(curl -s -X POST "${API_URL}/menus/${MENU_ID}/items" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Caesar Salad",
    "description": "Fresh romaine with caesar dressing",
    "price": "9.99",
    "dietary_info": "Vegetarian",
    "is_available": true,
    "display_order": 2
  }')

echo "$ITEM2" | grep -q "Menu item created successfully"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Menu item 2 created${NC}"
  ITEM2_ID=$(echo "$ITEM2" | python3 -c "import sys, json; print(json.load(sys.stdin)['item']['id'])")
  echo "  Item: Caesar Salad - \$9.99"
else
  echo -e "${RED}✗ Failed to create menu item 2${NC}"
fi
echo ""

# Test 7: Login as regular user
echo "7️⃣  Testing User Login..."
USER_LOGIN=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@motd.com",
    "password": "User123!"
  }')

echo "$USER_LOGIN" | grep -q "access_token"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ User login successful${NC}"
  USER_TOKEN=$(echo "$USER_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")
  echo "  Token: ${USER_TOKEN:0:20}..."
else
  echo -e "${RED}✗ User login failed${NC}"
  exit 1
fi
echo ""

# Test 8: Get available menus
echo "8️⃣  Testing Get Available Menus (User)..."
AVAILABLE_MENUS=$(curl -s "${API_URL}/menus/available?date=2026-02-11" \
  -H "Authorization: Bearer $USER_TOKEN")

echo "$AVAILABLE_MENUS" | grep -q "menus"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Available menus retrieved${NC}"
  MENU_COUNT=$(echo "$AVAILABLE_MENUS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['menus']))")
  echo "  Available menus for 2026-02-11: $MENU_COUNT"
else
  echo -e "${RED}✗ Failed to get available menus${NC}"
fi
echo ""

# Test 9: Get menu with items
echo "9️⃣  Testing Get Menu with Items..."
MENU_DETAIL=$(curl -s "${API_URL}/menus/${MENU_ID}" \
  -H "Authorization: Bearer $USER_TOKEN")

echo "$MENU_DETAIL" | grep -q "items"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Menu details retrieved${NC}"
  ITEM_COUNT=$(echo "$MENU_DETAIL" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['items']))")
  echo "  Menu items: $ITEM_COUNT"
  echo "$MENU_DETAIL" | python3 -c "import sys, json; d=json.load(sys.stdin); [print(f\"    - {item['name']}: \${item['price']}\") for item in d['items']]"
else
  echo -e "${RED}✗ Failed to get menu details${NC}"
fi
echo ""

# Test 10: Create an order (user)
echo "🔟 Testing Create Order (User)..."
ORDER=$(curl -s -X POST "${API_URL}/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d "{
    \"menu_id\": $MENU_ID,
    \"order_date\": \"2026-02-11\",
    \"items\": [
      {
        \"menu_item_id\": $ITEM1_ID,
        \"quantity\": 1,
        \"notes\": \"No mayo please\"
      },
      {
        \"menu_item_id\": $ITEM2_ID,
        \"quantity\": 1
      }
    ],
    \"notes\": \"Deliver to office 3A\"
  }")

echo "$ORDER" | grep -q "Order created successfully"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Order created${NC}"
  ORDER_ID=$(echo "$ORDER" | python3 -c "import sys, json; print(json.load(sys.stdin)['order']['id'])")
  TOTAL=$(echo "$ORDER" | python3 -c "import sys, json; print(json.load(sys.stdin)['order']['total_amount'])")
  echo "  Order ID: $ORDER_ID"
  echo "  Total: \$$TOTAL"
else
  echo -e "${RED}✗ Failed to create order${NC}"
  echo "$ORDER"
fi
echo ""

# Test 11: Get user's orders
echo "1️⃣1️⃣  Testing Get User Orders..."
USER_ORDERS=$(curl -s "${API_URL}/orders" \
  -H "Authorization: Bearer $USER_TOKEN")

echo "$USER_ORDERS" | grep -q "orders"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ User orders retrieved${NC}"
  ORDER_COUNT=$(echo "$USER_ORDERS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['orders']))")
  echo "  Total orders: $ORDER_COUNT"
else
  echo -e "${RED}✗ Failed to get user orders${NC}"
fi
echo ""

# Test 12: Get weekly orders
echo "1️⃣2️⃣  Testing Get Weekly Orders..."
WEEKLY=$(curl -s "${API_URL}/orders/week?start_date=2026-02-10" \
  -H "Authorization: Bearer $USER_TOKEN")

echo "$WEEKLY" | grep -q "weekly_orders"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Weekly orders retrieved${NC}"
  echo "$WEEKLY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for day in data['weekly_orders']:
    status = '✓ Ordered' if day['has_order'] else '✗ Missing'
    print(f\"  {day['date']}: {status}\")
"
else
  echo -e "${RED}✗ Failed to get weekly orders${NC}"
fi
echo ""

# Test 13: Get missing days
echo "1️⃣3️⃣  Testing Get Missing Order Days..."
MISSING=$(curl -s "${API_URL}/orders/missing-days?days_ahead=7&start_date=2026-02-10" \
  -H "Authorization: Bearer $USER_TOKEN")

echo "$MISSING" | grep -q "missing_dates"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Missing days retrieved${NC}"
  MISSING_COUNT=$(echo "$MISSING" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
  echo "  Missing order days: $MISSING_COUNT"
  echo "$MISSING" | python3 -c "import sys, json; [print(f\"    - {date}\") for date in json.load(sys.stdin)['missing_dates'][:5]]"
else
  echo -e "${RED}✗ Failed to get missing days${NC}"
fi
echo ""

# Test 14: Admin dashboard
echo "1️⃣4️⃣  Testing Admin Dashboard..."
DASHBOARD=$(curl -s "${API_URL}/admin/dashboard" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "$DASHBOARD" | grep -q "stats"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Admin dashboard retrieved${NC}"
  echo "$DASHBOARD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
stats = data['stats']
print(f\"  Total users: {stats['total_users']}\")
print(f\"  Total restaurants: {stats['total_restaurants']}\")
print(f\"  Total menus: {stats['total_menus']}\")
print(f\"  Orders today: {stats['orders_today']}\")
print(f\"  Orders this week: {stats['orders_this_week']}\")
"
else
  echo -e "${RED}✗ Failed to get admin dashboard${NC}"
fi
echo ""

# Test 15: Try to access admin endpoint as regular user (should fail)
echo "1️⃣5️⃣  Testing Authorization (User accessing Admin endpoint)..."
UNAUTHORIZED=$(curl -s "${API_URL}/admin/dashboard" \
  -H "Authorization: Bearer $USER_TOKEN")

echo "$UNAUTHORIZED" | grep -q "Admin access required"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Authorization working correctly (access denied)${NC}"
else
  echo -e "${RED}✗ Authorization not working (user should not access admin endpoint)${NC}"
fi
echo ""

echo "==============================="
echo -e "${GREEN}🎉 API Testing Complete!${NC}"
echo ""
echo "Test Credentials:"
echo "  Admin: admin@motd.com / Admin123!"
echo "  User:  user@motd.com / User123!"
echo ""
echo "API Base URL: http://localhost:5000/api"
