# ZeeTech Flask Backend

A Python Flask-based backend for the ZeeTech service booking application.

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and update with your configuration:

```bash
cp .env.example .env
```

## Running the Application

```bash
# Development
python run.py

# Production
FLASK_ENV=production python run.py
```

The application will start on `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/verify` - Verify JWT token

### Services

- `GET /api/services` - Get all services
- `GET /api/services/<id>` - Get service details
- `POST /api/services` - Create new service

### Bookings

- `GET /api/bookings` - Get all bookings
- `GET /api/bookings/<id>` - Get booking details
- `POST /api/bookings` - Create new booking

### Users

- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

### Ratings

- `POST /api/ratings` - Create new rating
- `GET /api/ratings/<id>` - Get rating details

## Health Check

```bash
curl http://localhost:5000/health
```

## Technologies

- **Framework**: Flask 3.0.0
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT
- **CORS**: Flask-CORS
- **Password Hashing**: bcrypt

## File Structure

```
backend/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── config.py         # Configuration
│   ├── routes/           # API route handlers
│   │   ├── auth.py
│   │   ├── services.py
│   │   ├── bookings.py
│   │   ├── users.py
│   │   └── ratings.py
│   ├── services/         # Business logic
│   │   └── auth_service.py
│   └── utils/            # Utilities
│       ├── supabase_client.py
│       └── helpers.py
├── run.py                # Entry point
├── requirements.txt      # Dependencies
└── .env                  # Environment variables
```

## Environment Variables

- `PORT` - Server port (default: 5000)
- `FLASK_ENV` - Environment (development/production)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `JWT_SECRET` - JWT signing secret
- `SERVER_URL` - Backend server URL
- `FRONTEND_URL` - Frontend application URL

## Development

```bash
# Install with dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Check code style
flake8 .
```

## License

ISC
