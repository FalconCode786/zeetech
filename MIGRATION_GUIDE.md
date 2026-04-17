# ZeeTech Migration Guide: Flask to Express.js Backend

This guide explains the successful migration from Flask to Express.js and how to run both the backend and frontend together.

## Overview

The ZeeTech project has been successfully migrated from Flask to Express.js:

- ✅ **Backend**: Migrated from Flask to Express.js with full feature parity
- ✅ **Database**: Maintained Supabase (PostgreSQL) as the database
- ✅ **Authentication**: JWT tokens + Session-based authentication
- ✅ **Frontend**: Flutter app remains compatible with Express backend

## Directory Structure

```
zeetech2/
├── backend/                # NEW: Express.js backend
│   ├── src/
│   │   ├── config/         # Configuration files
│   │   ├── middleware/     # Express middleware
│   │   ├── routes/         # API route handlers
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utility functions
│   │   └── index.js        # Main server entry point
│   ├── uploads/            # File uploads directory
│   ├── package.json        # Node.js dependencies
│   ├── .env.example        # Environment variables template
│   └── README.md           # Backend documentation
│
└── zeetech/                # Flutter frontend
    ├── lib/                # Flutter source code
    ├── pubspec.yaml        # Flutter dependencies
    └── ...
```

## Quick Start

### Prerequisites

- **Node.js 16+** (for backend)
- **npm or yarn** (for backend)
- **Flutter SDK** (for frontend)
- **Supabase account** with database setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Create .env file from template
cp .env.example .env

# Edit .env with your Supabase credentials:
# - SUPABASE_URL=your_supabase_url
# - SUPABASE_KEY=your_supabase_key
# - JWT_SECRET=generate_a_random_secret

# Run development server (with auto-reload)
npm run dev

# Server will start on http://localhost:5000
```

### 2. Frontend Setup

```bash
# Navigate to Flutter directory
cd zeetech

# Get dependencies
flutter pub get

# Run on your device/emulator
flutter run

# Or run on web
flutter run -d chrome
```

## API Endpoints

All API endpoints are available at `http://localhost:5000/api/`

### Key Endpoints

#### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/verify` - Verify current user
- `POST /api/auth/change-password` - Change password

#### Services

- `GET /api/services/categories` - Get service categories
- `GET /api/services/all` - List all services
- `GET /api/services/search` - Search services
- `POST /api/services/create` - Create service (provider only)

#### Bookings

- `POST /api/bookings` - Create booking
- `GET /api/bookings` - Get user's bookings
- `GET /api/bookings/:id` - Get booking details
- `PUT /api/bookings/:id` - Update booking status
- `DELETE /api/bookings/:id` - Cancel booking

#### Ratings

- `POST /api/ratings` - Create rating
- `GET /api/ratings/:bookingId` - Get booking rating

#### Users

- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/search` - Search providers

## Configuration

### Backend Environment Variables

Create `backend/.env` with:

```env
# Server
PORT=5000
NODE_ENV=development

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# JWT
JWT_SECRET=your-very-secure-random-string

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:8080
SERVER_URL=http://localhost:5000
```

### Frontend Configuration

Update in `zeetech/lib/core/constants/app_constants.dart`:

```dart
// Change baseUrl based on where you're running:

// For local development:
static const String baseUrl = 'http://192.168.18.131:5000';

// For Android Emulator:
static const String baseUrl = 'http://10.0.2.2:5000';

// For production:
static const String baseUrl = 'https://your-production-server.com';
```

## Features

### Backend Features

- ✅ User registration & authentication
- ✅ JWT token-based security
- ✅ Role-based access control (customer, provider, admin)
- ✅ Service marketplace
- ✅ Booking management
- ✅ Rating & feedback system
- ✅ Payment integration (Stripe)
- ✅ File uploads
- ✅ CORS configured for mobile & web
- ✅ Input validation
- ✅ Error handling
- ✅ Rate limiting

### Frontend Features

- ✅ User authentication
- ✅ Service browsing & search
- ✅ Booking creation & management
- ✅ Provider ratings
- ✅ Payment processing
- ✅ User profiles
- ✅ Real-time notifications (ready to implement)

## Running in Different Environments

### Local Development

```bash
# Terminal 1: Backend
cd backend
npm run dev
# Output: Server running on http://localhost:5000

# Terminal 2: Flutter (Web)
cd zeetech
flutter run -d chrome
# App will connect to http://localhost:5000

# Terminal 3: Flutter (Mobile on same network)
cd zeetech
flutter run
# Ensure baseUrl points to your machine's IP: http://192.168.18.131:5000
```

### Production Deployment

1. **Backend Deployment**:

   ```bash
   npm install --production
   npm start
   ```

2. **Flutter Build**:

   ```bash
   flutter build apk      # Android
   flutter build ios      # iOS
   flutter build web      # Web
   ```

## Troubleshooting

### Backend Connection Issues

**Problem**: "Connection refused" error when Flutter tries to connect

**Solution**:

1. Verify backend is running: `curl http://localhost:5000/health`
2. Check firewall settings
3. Ensure correct IP address in Flutter app constants
4. For physical device, use machine IP instead of localhost

### Supabase Connection

**Problem**: "Database not initialized"

**Solution**:

1. Verify SUPABASE_URL and SUPABASE_KEY in `.env`
2. Check Supabase project is active
3. Ensure database tables are created (run migrations)

### CORS Issues

**Problem**: "CORS policy blocked" error

**Solution**:

1. Backend CORS is configured to allow all origins
2. Check that frontend is making requests correctly
3. Ensure Authorization header is being sent

### Flutter API Calls Failing

**Problem**: API returns 401 Unauthorized

**Solution**:

1. Ensure token is saved after login
2. Check token is being sent in Authorization header
3. Verify JWT_SECRET matches between backend and frontend

## Response Format

All API responses follow this format:

### Success Response

```json
{
  "message": "Operation successful",
  "data": { /* response data */ }
}
```

### Error Response

```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  phone VARCHAR UNIQUE NOT NULL,
  fullName VARCHAR NOT NULL,
  role VARCHAR (customer/provider/admin),
  password VARCHAR NOT NULL,
  profileImage TEXT,
  address VARCHAR,
  city VARCHAR,
  area VARCHAR,
  rating FLOAT DEFAULT 0,
  totalReviews INT DEFAULT 0,
  status VARCHAR (active/inactive),
  emailVerified BOOLEAN,
  phoneVerified BOOLEAN,
  createdAt TIMESTAMP,
  updatedAt TIMESTAMP
);
```

Similar schema for: services, bookings, ratings, feedbacks tables.

## Development Tips

1. **Debug Backend**: Enable logging in console

   ```bash
   npm run dev  # Shows all requests
   ```

2. **Debug Flutter**: Check logs in VS Code terminal

   ```
   [API] GET http://192.168.18.131:5000/api/auth/verify
   ```

3. **Test API Endpoints**: Use curl or Postman

   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"Password123!"}'
   ```

## Next Steps

1. ✅ **Setup Backend** - Done! Express server running
2. ✅ **Setup Frontend** - Flutter app configured
3. 📝 **Run Both Together** - Follow Quick Start above
4. 🔧 **Customize** - Add your business logic
5. 🚀 **Deploy** - Push to production server

## Support & Resources

- **Backend Docs**: `backend/README.md`
- **API Docs**: `backend/API_DOCUMENTATION.md` (to be created)
- **Flutter Setup**: Official Flutter docs at flutter.dev
- **Supabase Docs**: supabase.com/docs

## Key Changes from Flask

| Feature | Flask | Express.js |
|---------|-------|-----------|
| Framework | Flask | Express |
| Language | Python | JavaScript/Node.js |
| Dependencies | pip/requirements.txt | npm/package.json |
| Run Server | `python run.py` | `npm start` or `npm run dev` |
| Middleware | Decorators | Middleware functions |
| Validation | Custom | Joi validation |
| Structure | Blueprints | Router modules |

## Conclusion

The backend has been successfully migrated from Flask to Express.js while maintaining full API compatibility with the Flutter frontend. Both applications are now running on modern, maintainable technology stacks and are ready for production deployment.

For questions or issues, refer to the respective README files in the backend and frontend directories.
