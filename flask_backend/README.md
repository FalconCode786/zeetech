# ZeeTech Flask Backend

A Flask-based REST API for a service booking marketplace application. Supports user authentication, service catalog management, booking lifecycle, ratings, payments (Stripe), and admin features.

## Project Structure

```
flask_backend/
├── app/
│   ├── __init__.py              # Flask app factory, MongoDB initialization
│   ├── config.py                # Configuration management (dev/prod/test)
│   ├── models/                  # Database models and schemas
│   ├── routes/                  # API route blueprints
│   ├── services/                # Business logic services
│   └── utils/
│       ├── errors.py            # Custom exceptions and error handlers
│       ├── decorators.py        # Auth and role decorators
│       ├── helpers.py           # Utility functions
│       └── __init__.py
├── tests/                       # Unit and integration tests
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- pip (Python package manager)

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd flask_backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings
# - Set MONGODB_URI to your MongoDB connection string
# - Set SECRET_KEY to a secure random string
# - Add Stripe API keys if integrating payments
# - Configure email settings if using notifications
```

### 5. Verify MongoDB Connection

Make sure MongoDB is running locally or update `MONGODB_URI` in `.env` to point to your MongoDB instance.

### 6. Run the Application

```bash
python run.py
```

The server will start on `http://localhost:5000`

### 7. Verify Server is Running

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "healthy",
  "message": "ZeeTech Backend is running"
}
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | No | `development`, `production`, or `testing` (default: development) |
| `SECRET_KEY` | Yes | Flask secret key for sessions |
| `MONGODB_URI` | Yes | MongoDB connection string |
| `MONGODB_DB_NAME` | No | MongoDB database name (default: zeetech) |
| `STRIPE_SECRET_KEY` | No | Stripe API secret key for payments |
| `STRIPE_PUBLISHABLE_KEY` | No | Stripe publishable key |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook signing secret |
| `MAIL_SERVER` | No | SMTP server for email notifications |
| `MAIL_PORT` | No | SMTP port (usually 587 for TLS) |
| `MAIL_USERNAME` | No | Email account username |
| `MAIL_PASSWORD` | No | Email account password |
| `FRONTEND_URL` | No | Flutter frontend URL for CORS |
| `UPLOAD_FOLDER` | No | Directory for file uploads (default: uploads) |

## API Endpoints

### Health Check

- `GET /health` - Server health check

### Authentication (Phase 3)

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/verify` - Verify authenticated user

### Users (Phase 3)

- `GET /api/users/<userId>` - Get user profile
- `PUT /api/users/<userId>` - Update user profile
- `GET /api/users/<userId>/ratings` - Get provider ratings

### Services (Phase 4)

- `GET /api/services/categories` - List service categories
- `GET /api/services/categories/<categoryId>` - Get category details
- `GET /api/services/categories/<categoryId>/subcategories` - List subcategories

### Bookings (Phase 5)

- `POST /api/bookings` - Create booking
- `GET /api/bookings` - List user's bookings
- `GET /api/bookings/<bookingId>` - Get booking details
- `PUT /api/bookings/<bookingId>` - Update booking status

### Ratings (Phase 6)

- `POST /api/bookings/<bookingId>/rate` - Rate completed booking
- `GET /api/users/<userId>/ratings` - Get provider ratings

### Payments (Phase 7)

- `POST /api/payments/create-intent` - Create Stripe payment intent
- `POST /api/payments/webhook` - Stripe webhook handler

### Admin (Phase 7)

- `POST /api/admin/categories` - Create service category
- `PUT /api/admin/categories/<categoryId>` - Edit category
- `DELETE /api/admin/categories/<categoryId>` - Delete category
- `GET /api/admin/bookings` - View all bookings (admin only)
- `GET /api/admin/users` - List all users (admin only)

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_auth.py

# Run with coverage
python -m pytest --cov=app tests/
```

## Development Workflow

### Code Style

- Follow PEP 8 style guide
- Use type hints where possible
- Document functions with docstrings

### Logging

- Use `app.logger` for logging
- Avoid printing debug information directly

### Database

- Use MongoDB transactions for multi-document operations
- Create indexes on frequently queried fields
- Use schema validation for consistency

## Deployment

### Production Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Enable `SESSION_COOKIE_SECURE=True` for HTTPS
4. Use environment-specific configuration
5. Set up proper logging and monitoring

Example with Gunicorn:

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 "app:create_app()"
```

### Docker Deployment

A Dockerfile and docker-compose.yml can be added for containerized deployment.

## Troubleshooting

### MongoDB Connection Failed

- Ensure MongoDB is running
- Check `MONGODB_URI` in `.env`
- Verify network connectivity

### Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

- Change `FLASK_PORT` in `.env`
- Or kill process using port 5000

## Contributing

1. Create a feature branch
2. Make changes and test thoroughly
3. Create a pull request with description

## License

Proprietary - ZeeTech

## Support

For issues or questions, contact the development team.

---

**Implementation Progress:**

- [x] Phase 1: Project Setup & Core Infrastructure
- [ ] Phase 2: Database Models & MongoDB
- [ ] Phase 3: Authentication & User Management
- [ ] Phase 4: Service Catalog API
- [ ] Phase 5: Booking Management
- [ ] Phase 6: Ratings & Reviews
- [ ] Phase 7: Admin & Advanced Features
- [ ] Phase 8: Error Handling & Logging
- [ ] Phase 9: Testing & Documentation
