# Meal of the Day (MOTD)

A web application for companies to streamline employee lunch ordering with automated WhatsApp reminders and restaurant order management.

## Features

### User Features
- **Employee Ordering**: Users can order meals for the week ahead
- **Weekly Calendar View**: Visual 7-day dashboard with color-coded order status
- **Order Placement**: Browse menus, add items to cart, place orders with special instructions
- **Order Management**: View order details, cancel pending orders
- **Profile Management**: Update personal information, change password
- **Mobile-Friendly**: Fully responsive design optimized for mobile ordering

### Admin Features
- **Dashboard**: Real-time statistics (orders, users, revenue)
- **Restaurant Management**: CRUD operations for restaurants and menus
- **Order Tracking**: View all orders, update statuses, monitor fulfillment
- **User Insights**: Track users without orders, send targeted reminders

### Automation
- **WhatsApp Reminders**: Automated reminders for users who haven't ordered
- **Email Summaries**: Automated order summaries sent to restaurants
- **Background Jobs**: Scheduled tasks for reminders and order processing

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL (SQLite for development)
- **ORM**: SQLAlchemy
- **Authentication**: JWT (Flask-JWT-Extended)
- **Validation**: Marshmallow
- **Migrations**: Flask-Migrate (Alembic)
- **Scheduler**: APScheduler
- **Email**: SendGrid
- **WhatsApp**: WhatsApp Cloud API

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Routing**: React Router 6
- **HTTP Client**: Axios
- **Icons**: lucide-react
- **Date Handling**: date-fns

## Project Structure

```
motd/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration
│   ├── models/               # Database models
│   ├── routes/               # API endpoints
│   ├── services/             # Business logic
│   ├── schemas/              # Validation schemas
│   ├── middleware/           # Auth & error handling
│   ├── utils/                # Helper functions
│   └── tasks/                # Background jobs
├── migrations/               # Database migrations
├── tests/                    # Test suite
├── frontend/                 # React frontend
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── .env                      # Local environment (git-ignored)
├── wsgi.py                   # WSGI entry point
├── manage.py                 # Management CLI
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL (or SQLite for development)
- Node.js 18+ (for frontend)
- WhatsApp Business Account (for production)
- SendGrid Account (for email)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd motd
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   # Initialize migrations (first time only)
   flask db init
   
   # Create migration
   flask db migrate -m "Initial migration"
   
   # Apply migration
   flask db upgrade
   ```

6. **Create admin user**
   ```bash
   python manage.py create-admin
   ```

7. **Run development server**
   ```bash
   flask run
   ```

   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default: http://localhost:5000/api)
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### Quick Setup Script

```bash
# One-line setup for development
python -m venv venv && source venv/bin/activate && \
pip install -r requirements.txt && \
flask db init && flask db migrate -m "Initial migration" && \
flask db upgrade && python manage.py create-admin
```

## API Documentation

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {...}
}
```

### Orders

#### Create Order
```http
POST /api/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "menu_id": 1,
  "order_date": "2026-02-10",
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 1,
      "notes": "No onions"
    }
  ],
  "notes": "Deliver to office 3A"
}
```

#### Get Weekly Orders
```http
GET /api/orders/week?start_date=2026-02-10
Authorization: Bearer <token>

Response:
{
  "weekly_orders": [
    {
      "date": "2026-02-10",
      "has_order": true,
      "order": {...}
    },
    ...
  ]
}
```

#### Get Missing Days
```http
GET /api/orders/missing-days?days_ahead=7
Authorization: Bearer <token>

Response:
{
  "missing_dates": ["2026-02-11", "2026-02-12"],
  "count": 2
}
```

### Admin Endpoints

All admin endpoints require `Authorization: Bearer <admin_token>`

- `GET /api/admin/dashboard` - Dashboard statistics
- `GET /api/admin/orders` - All orders with filters
- `GET /api/admin/orders/summary` - Order summary by date range
- `PUT /api/admin/orders/:id/status` - Update order status
- `POST /api/admin/orders/send-to-restaurant` - Send orders to restaurant
- `GET /api/admin/users-without-orders` - Users missing orders

### Full API Reference

See [API.md](API.md) for complete API documentation.

## Background Jobs

The application uses APScheduler for automated tasks:

### Daily Reminder Job (10:00 AM)
- Identifies users without orders for upcoming days
- Sends WhatsApp reminders via template messages
- Logs reminder status in database

### Restaurant Order Summary (11:00 AM)
- Aggregates orders by restaurant for the day
- Generates formatted email with order details
- Sends to restaurant contact email
- Tracks delivery status

### Session Cleanup (Midnight)
- Removes expired JWT sessions from database

Configure schedule times in `.env`:
```env
REMINDER_TIME=10:00
RESTAURANT_SUMMARY_TIME=11:00
REMINDER_DAYS_AHEAD=1,2,3
```

## External Services Setup

### WhatsApp Cloud API

1. Create Meta Business Account at https://business.facebook.com
2. Set up WhatsApp Business Platform
3. Create and verify phone number
4. Create message template (requires Meta approval):

```
Hello {{1}},
You haven't ordered lunch for {{2}} yet!
Order now: {{3}}
```

5. Add credentials to `.env`:
```env
WHATSAPP_API_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id
```

### SendGrid Email

1. Create account at https://sendgrid.com
2. Generate API key
3. Verify sender email
4. Add to `.env`:
```env
SENDGRID_API_KEY=your_api_key
FROM_EMAIL=noreply@yourdomain.com
```

### Database (Supabase PostgreSQL)

1. Create account at https://supabase.com
2. Create new project
3. Get connection string
4. Add to `.env`:
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## Deployment

### Code Capsules

1. **Prepare for deployment**
   ```bash
   # Ensure requirements.txt is up to date
   pip freeze > requirements.txt
   
   # Commit changes
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Create Code Capsules account**
   - Sign up at https://codecapsules.io

3. **Create backend capsule**
   - Connect GitHub repository
   - Select Python/Flask runtime
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn wsgi:app`

4. **Configure environment variables**
   - Add all variables from `.env` to capsule settings
   - Update `DATABASE_URL` with production database
   - Update `FRONTEND_URL` with production URL

5. **Add database**
   - Use Supabase PostgreSQL or Code Capsules add-on
   - Run migrations: `flask db upgrade`

6. **Deploy**
   - Push to GitHub triggers automatic deployment
   - Monitor logs for errors

7. **Deploy frontend (optional separate capsule)**
   - Create static capsule from GitHub repository
   - Set build command: `cd frontend && npm install && npm run build`
   - Set publish directory: `frontend/dist`
   - Add environment variable: `VITE_API_BASE_URL=https://your-backend-url/api`
   - Deploy

### Post-Deployment

1. Create admin user (via Code Capsules console):
   ```bash
   python manage.py create-admin
   ```

2. Test endpoints:
   ```bash
   curl https://your-app.codecapsules.co.za/api/auth/register
   ```

3. Configure WhatsApp webhook:
   - Point to `https://your-app.codecapsules.co.za/api/webhooks/whatsapp`

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

### Database Management

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Reset database (destroys data!)
python manage.py reset
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

## Troubleshooting

### Database Issues

**Error: "No such table"**
```bash
flask db upgrade
```

**Error: "Database is locked"**
- SQLite issue in development
- Close other connections or switch to PostgreSQL

### Authentication Issues

**Error: "Token has expired"**
- JWT tokens expire after 1 hour
- Re-authenticate to get new token

**Error: "Invalid token"**
- Ensure `JWT_SECRET_KEY` is consistent
- Check token format: `Bearer <token>`

### WhatsApp Issues

**Error: "WhatsApp not configured"**
- Add credentials to `.env`
- Verify template is approved in Meta Business

**Error: "Template not found"**
- Create and approve template in Meta Business Manager
- Match template name in code

### Email Issues

**Error: "Email not configured"**
- Add SendGrid API key to `.env`
- Verify sender email in SendGrid

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/motd/issues)
- Email: support@mealoftheday.com

## Roadmap

- [x] Complete React frontend
- [x] User authentication and profile management
- [x] Weekly order calendar view
- [x] Order placement with shopping cart
- [x] Admin dashboard with statistics
- [x] Mobile-responsive design
- [ ] Mobile app (React Native)
- [ ] PDF receipt generation
- [ ] Multi-language support
- [ ] Payment integration
- [ ] Advanced analytics dashboard
- [ ] Dietary preference filtering
- [ ] Favorite orders
- [ ] Order history export
- [ ] Real-time order updates (WebSocket)
- [ ] Push notifications for order status

## Acknowledgments

- Flask framework and ecosystem
- SendGrid for email service
- Meta for WhatsApp Business API
- Code Capsules for hosting
- Supabase for PostgreSQL database
