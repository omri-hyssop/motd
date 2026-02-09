# MOTD Frontend

React frontend for Meal of the Day - a company lunch ordering system.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework
- **date-fns** - Date manipulation
- **lucide-react** - Icon library

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/              # Authentication components
│   │   ├── orders/            # Order-related components
│   │   ├── menus/             # Menu components
│   │   ├── admin/             # Admin components
│   │   └── common/            # Shared components (Navbar, Loading, etc.)
│   ├── pages/
│   │   ├── LoginPage.jsx      # Login page
│   │   ├── RegisterPage.jsx   # Registration page
│   │   ├── HomePage.jsx       # User dashboard (weekly orders)
│   │   ├── OrderPage.jsx      # Order placement page
│   │   ├── OrderDetailPage.jsx # View order details
│   │   ├── ProfilePage.jsx    # User profile management
│   │   └── AdminDashboard.jsx # Admin dashboard
│   ├── services/
│   │   ├── api.js             # Axios instance with interceptors
│   │   ├── authService.js     # Authentication API calls
│   │   ├── orderService.js    # Order API calls
│   │   ├── menuService.js     # Menu API calls
│   │   └── restaurantService.js # Restaurant API calls
│   ├── context/
│   │   └── AuthContext.jsx    # Global authentication state
│   ├── App.jsx                # Main app component with routing
│   ├── main.jsx               # Entry point
│   └── index.css              # Global styles with Tailwind
├── index.html                 # HTML template
├── vite.config.js             # Vite configuration
├── tailwind.config.js         # Tailwind configuration
├── postcss.config.js          # PostCSS configuration
├── .eslintrc.cjs              # ESLint configuration
└── package.json               # Dependencies and scripts
```

## Features

### User Features
- **Authentication**: Login, registration, logout with JWT tokens
- **Weekly Order View**: Visual calendar showing orders for the week
- **Order Placement**: Browse menus, add items to cart, place orders
- **Order Management**: View order details, cancel pending orders
- **Profile Management**: Update profile information, change password

### Admin Features
- **Dashboard**: Overview of orders, users, and revenue statistics
- **Order Management**: View all orders, update statuses
- **Restaurant Management**: CRUD operations for restaurants
- **Menu Management**: CRUD operations for menus and menu items

## Setup Instructions

### Prerequisites
- Node.js 20+ and npm
- Backend server running on `http://localhost:5000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Building for Production

Build the application:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

### Linting

Run ESLint:
```bash
npm run lint
```

## API Integration

The frontend communicates with the Flask backend through the services layer. All API calls are authenticated using JWT tokens stored in localStorage.

### API Service (`services/api.js`)
- Axios instance with base URL configuration
- Request interceptor adds JWT token to headers
- Response interceptor handles 401 errors (token expiration)

### Authentication Flow
1. User logs in via `LoginPage`
2. Backend returns JWT token and user data
3. Token stored in `localStorage`
4. `AuthContext` manages global auth state
5. All subsequent API calls include token in Authorization header
6. Protected routes redirect to login if not authenticated

## Styling

The app uses Tailwind CSS with custom utility classes defined in `index.css`:

- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary buttons
- `.btn-danger` - Destructive actions
- `.card` - Card containers
- `.input` - Form inputs
- `.label` - Form labels

## Mobile Responsiveness

All pages are mobile-friendly with responsive layouts:
- Mobile-first design approach
- Collapsible navigation menu on mobile
- Grid layouts adapt to screen size
- Touch-friendly buttons and interactions

## Protected Routes

Routes are protected using the `ProtectedRoute` component:

```jsx
<Route
  path="/admin"
  element={
    <ProtectedRoute requireAdmin>
      <AdminDashboard />
    </ProtectedRoute>
  }
/>
```

- `ProtectedRoute` checks authentication status
- Shows loading spinner while checking auth
- Redirects to `/login` if not authenticated
- `requireAdmin` prop restricts access to admin users

## State Management

### Global State
- **AuthContext**: User authentication state, login/logout functions
- Accessible via `useAuth()` hook throughout the app

### Local State
- Component-level state with `useState`
- API data fetched with `useEffect`
- Form state managed locally in components

## Testing the Frontend

### Manual Testing Checklist

**Authentication:**
- [ ] User can register with valid data
- [ ] User can log in with correct credentials
- [ ] User is redirected to home after login
- [ ] Logout clears auth state and redirects to login
- [ ] Protected routes redirect unauthenticated users

**Weekly Order View:**
- [ ] Dashboard shows 7 days
- [ ] Days with orders show green indicators
- [ ] Days without orders show red indicators
- [ ] Clicking "Order Now" navigates to order page
- [ ] Clicking existing order shows order details

**Order Placement:**
- [ ] Available menus load for selected date
- [ ] Menu items can be added to cart
- [ ] Cart shows correct quantities and totals
- [ ] Order submission creates order successfully
- [ ] User redirected to home after successful order

**Profile Management:**
- [ ] Profile page shows user information
- [ ] User can edit and save profile changes
- [ ] Password change works with correct current password
- [ ] Email cannot be changed

**Admin Dashboard:**
- [ ] Dashboard shows statistics (orders, users, revenue)
- [ ] Recent orders table displays correctly
- [ ] Admin can navigate to management pages
- [ ] Regular users cannot access admin routes

## Deployment

### Vite Build Output
The `npm run build` command creates optimized production files in the `dist/` directory.

### Deployment Options

**1. Code Capsules (Static Site)**
- Create static capsule
- Set build command: `npm run build`
- Set publish directory: `dist`
- Deploy

**2. Netlify**
- Connect GitHub repository
- Build command: `npm run build`
- Publish directory: `dist`
- Environment variables: `VITE_API_BASE_URL`

**3. Vercel**
- Import project from GitHub
- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`

### Environment Variables for Production

Update `VITE_API_BASE_URL` to point to your production backend:
```env
VITE_API_BASE_URL=https://your-backend.codecapsules.co.za/api
```

## Troubleshooting

### CORS Errors
- Ensure Flask backend has CORS configured for your frontend domain
- Check `app/__init__.py` for CORS settings

### 401 Unauthorized Errors
- Token may have expired (default 1 hour)
- Clear localStorage and log in again
- Check backend JWT configuration

### Vite Proxy Not Working
- Ensure backend is running on `http://localhost:5000`
- Check `vite.config.js` proxy configuration
- Restart Vite dev server after config changes

### Build Errors
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf .vite`
- Check for TypeScript errors if using `.tsx` files

## Future Enhancements

- [ ] Add loading skeletons for better UX
- [ ] Implement toast notifications
- [ ] Add order search and filtering
- [ ] Implement pagination for long lists
- [ ] Add dark mode support
- [ ] Implement PWA features (offline support, push notifications)
- [ ] Add order history export (CSV/PDF)
- [ ] Implement real-time order status updates (WebSocket)

## Contributing

When adding new features:
1. Create reusable components in `components/common/`
2. Keep services focused on API calls only
3. Use Tailwind utility classes for styling
4. Follow existing naming conventions
5. Keep components small and focused

## License

MIT
