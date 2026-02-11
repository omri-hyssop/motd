# Meal of the Day (MOTD)

A web application for companies to streamline employee lunch ordering with automated WhatsApp reminders and restaurant order management.

## 🌐 Live Application

| Environment | URL | Status |
|-------------|-----|--------|
| **Frontend** | https://emss-487012.web.app | ✅ Live |
| **Backend API** | https://motd-backend-1008906809776.us-central1.run.app | ✅ Live |

**Deployment**: Automated via Cloud Build on push to `main` branch

---

## 🚀 Quick Start

### For Users
Visit the live application at https://emss-487012.web.app

### For Developers
See [Getting Started](#getting-started) section below for local development setup

### For DevOps
See [docs/CICD_QUICKSTART.md](./docs/CICD_QUICKSTART.md) for deployment setup

---

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
│   ├── src/                  # React source code
│   ├── Dockerfile            # Frontend container
│   └── .env.production       # Production config
├── docs/                     # Documentation
│   ├── README.md             # Documentation index
│   ├── CICD_QUICKSTART.md    # CI/CD quick start
│   ├── CICD_SETUP.md         # Complete CI/CD guide
│   ├── DEPLOYMENT_SUMMARY.md # Architecture overview
│   ├── DEVOPS_GCP_SETUP.md   # GCP infrastructure
│   └── DOCKER_DEPLOY.md      # Docker guide
├── cloudbuild-backend.yaml   # Backend CI/CD pipeline
├── cloudbuild-frontend.yaml  # Frontend CI/CD pipeline
├── firebase.json             # Firebase Hosting config
├── .firebaserc               # Firebase project config
├── Dockerfile                # Backend container
├── docker-compose.yml        # Local Docker setup
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── wsgi.py                   # WSGI entry point
├── manage.py                 # Management CLI
├── deploy-frontend.sh        # Frontend deploy script
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

All API endpoints are available at the backend URL: `https://motd-backend-1008906809776.us-central1.run.app/api`

For complete API documentation, see the route files in `app/routes/`.

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

## 📖 Documentation

Complete documentation is available in the [`docs/`](./docs/) directory:

- **[docs/README.md](./docs/README.md)** - Documentation index and quick links
- **[docs/CICD_QUICKSTART.md](./docs/CICD_QUICKSTART.md)** - 5-minute CI/CD setup
- **[docs/DEPLOYMENT_SUMMARY.md](./docs/DEPLOYMENT_SUMMARY.md)** - Architecture overview
- **[docs/CICD_SETUP.md](./docs/CICD_SETUP.md)** - Complete CI/CD reference
- **[docs/DEVOPS_GCP_SETUP.md](./docs/DEVOPS_GCP_SETUP.md)** - GCP infrastructure setup
- **[docs/DOCKER_DEPLOY.md](./docs/DOCKER_DEPLOY.md)** - Docker deployment guide

## Deployment

### Current Production Setup

**Infrastructure**:
- **Backend**: Cloud Run (containerized Flask app)
- **Frontend**: Firebase Hosting (static React build)
- **Database**: Supabase PostgreSQL
- **CI/CD**: Cloud Build + GitHub
- **Secrets**: Secret Manager
- **Scheduler**: Cloud Scheduler (for background jobs)

**Automatic Deployment**:
```bash
# Simply push to main branch
git push origin main
```

Cloud Build automatically:
1. Builds and pushes Docker images
2. Deploys backend to Cloud Run
3. Builds and deploys frontend to Firebase Hosting

**Manual Deployment**:
```bash
# Backend
docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/emss-487012/motd/motd-backend:latest .
docker push us-central1-docker.pkg.dev/emss-487012/motd/motd-backend:latest
gcloud run deploy motd-backend --image=us-central1-docker.pkg.dev/emss-487012/motd/motd-backend:latest --region=us-central1

# Frontend
./deploy-frontend.sh
```

### Setting Up CI/CD

See [docs/CICD_QUICKSTART.md](./docs/CICD_QUICKSTART.md) for complete setup instructions.

### Production Notes

- **Cloud Run**: Configured to listen on `$PORT` environment variable
- **Scheduler**: APScheduler disabled in web instances (`SCHEDULER_ENABLED=false`). Cloud Scheduler calls `/api/tasks/run` endpoint instead
- **File Uploads**: Stored in local `uploads/` directory (consider migrating to GCS for multi-instance deployments)
- **Secrets**: Managed via Secret Manager (DATABASE_URL, JWT keys, API tokens)
- **Access Control**: Backend is private, frontend is public via Firebase Hosting

### Post-Deployment

1. **Verify deployment**:
   ```bash
   # Check backend health
   curl https://motd-backend-1008906809776.us-central1.run.app/health

   # Visit frontend
   open https://emss-487012.web.app
   ```

2. **Create admin user** (if not already done):
   ```bash
   # Connect to Cloud Run instance or run migration job
   python manage.py create-admin
   ```

3. **Configure WhatsApp webhook**:
   - Point to: `https://motd-backend-1008906809776.us-central1.run.app/api/webhooks/whatsapp`

4. **Set up Cloud Scheduler** (for background jobs):
   - Already configured to call `/api/tasks/run` endpoint
   - See [docs/DEVOPS_GCP_SETUP.md](./docs/DEVOPS_GCP_SETUP.md) for details

5. **Monitor deployments**:
   - Cloud Build: https://console.cloud.google.com/cloud-build/builds?project=emss-487012
   - Cloud Run: https://console.cloud.google.com/run?project=emss-487012
   - Firebase: https://console.firebase.google.com/project/emss-487012

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

### ✅ Completed
- [x] Complete React frontend with Vite and Tailwind CSS
- [x] User authentication and profile management
- [x] Weekly order calendar view
- [x] Order placement with shopping cart
- [x] Admin dashboard with statistics
- [x] Mobile-responsive design
- [x] Production deployment on GCP (Cloud Run + Firebase Hosting)
- [x] CI/CD pipeline with Cloud Build + GitHub
- [x] Docker containerization
- [x] Automated testing (76 tests passing)
- [x] MOTD (Message of the Day) management
- [x] Restaurant availability scheduling
- [x] Email order summaries to restaurants
- [x] WhatsApp reminder integration

### 🚧 In Progress
- [ ] Enhanced admin features
- [ ] Order analytics and reporting

### 📋 Planned
- [ ] Mobile app (React Native)
- [ ] PDF receipt generation
- [ ] Multi-language support
- [ ] Payment integration
- [ ] Advanced analytics dashboard
- [ ] Dietary preference filtering
- [ ] Favorite orders and repeat ordering
- [ ] Order history export
- [ ] Real-time order updates (WebSocket)
- [ ] Push notifications for order status
- [ ] User feedback and ratings
- [ ] Restaurant menu versioning

## Acknowledgments

- Flask framework and ecosystem
- React and Vite for frontend tooling
- Tailwind CSS for styling
- SendGrid for email service
- Meta for WhatsApp Business API
- Google Cloud Platform for infrastructure (Cloud Run, Cloud Build, Secret Manager)
- Firebase for static hosting
- Supabase for PostgreSQL database
- GitHub for version control and CI/CD integration
