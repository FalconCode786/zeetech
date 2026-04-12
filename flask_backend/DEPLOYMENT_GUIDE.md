# ZeeTech Flask Backend - Deployment Guide

This guide covers deploying the ZeeTech Flask backend to production environments.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Local Development](#local-development)
- [Deployment Options](#deployment-options)
  - [Docker Deployment](#docker-deployment)
  - [Heroku Deployment](#heroku-deployment)
  - [AWS Deployment](#aws-deployment)
  - [DigitalOcean Deployment](#digitalocean-deployment)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Security Considerations](#security-considerations)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

- [ ] All tests passing: `pytest tests/`
- [ ] No hardcoded credentials in code
- [ ] Environment variables configured for production
- [ ] Database migrations completed
- [ ] SSL certificate obtained (for HTTPS)
- [ ] Domain name configured
- [ ] Stripe production keys obtained
- [ ] Email service configured (SendGrid, Gmail, etc.)
- [ ] Backup strategy in place
- [ ] Monitoring and alerting configured
- [ ] Rate limiting configured
- [ ] CORS settings restricted to frontend domain

## Local Development

### Setup

```bash
# Clone repository
git clone <repository-url>
cd flask_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with local values

# Run application
python run.py
```

The server runs on `http://localhost:5000` with hot reloading.

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

---

## Deployment Options

### Docker Deployment

#### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongo_data:/data/db

  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MONGODB_URI=mongodb://admin:password@mongodb:27017/zeetech?authSource=admin
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
    depends_on:
      - mongodb
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads

volumes:
  mongo_data:
```

#### Build and Run

```bash
# Build image
docker build -t zeetech-backend .

# Run container
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e MONGODB_URI=mongodb://localhost:27017/zeetech \
  -e SECRET_KEY=your-secret-key \
  zeetech-backend

# Or use docker-compose
docker-compose up -d
```

---

### Heroku Deployment

#### Prepare Application

```bash
# Install Procfile (tells Heroku how to run app)
# Create Procfile
echo "web: gunicorn run:app" > Procfile

# Create runtime.txt to specify Python version
echo "python-3.11.0" > runtime.txt
```

#### Deploy

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create zeetech-backend

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secure-key
heroku config:set MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/zeetech

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

#### MongoDB Atlas (Cloud MongoDB)

1. Create account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Add IP address to whitelist
4. Create database user
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/zeetech`

---

### AWS Deployment

#### Using Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.11 zeetech-backend --region us-east-1

# Create environment and deploy
eb create zeetech-env
eb deploy

# View logs
eb logs

# Set environment variables
eb setenv FLASK_ENV=production SECRET_KEY=your-key MONGODB_URI=mongodb://...

# Open application
eb open
```

#### Using EC2

```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx

# Clone repository
git clone <repo-url>
cd flask_backend

# Setup Python venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create .env file
nano .env
# Add environment variables

# Start with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app

# Configure Nginx as reverse proxy (see Nginx setup below)
```

---

### DigitalOcean Deployment

#### Using App Platform

1. Connect GitHub repository
2. Select Python framework
3. Set environment variables:
   - `FLASK_ENV=production`
   - `MONGODB_URI=your-mongodb-uri`
   - `SECRET_KEY=your-secret-key`
4. Configure health check: `GET /health`
5. Deploy

#### Using Droplet

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Follow EC2 setup above (same as AWS EC2)

# Install MongoDB locally or use DigitalOcean Managed Database
# Then configure MONGODB_URI accordingly
```

---

## Database Setup

### MongoDB Atlas (Recommended)

1. Visit [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create account
3. Create cluster (M0 free tier for testing)
4. Create database user
5. Get connection string
6. In `.env`: `MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/zeetech`

### Self-Hosted MongoDB

#### Ubuntu/Debian

```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify running
mongo --eval "db.adminCommand('ping')"
```

#### Docker

```bash
docker run -d \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -v mongo_data:/data/db \
  mongo:6.0
```

---

## Environment Configuration

### Production .env Example

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=use-a-very-long-random-key-here-minimum-32-characters

# MongoDB
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/zeetech?retryWrites=true&w=majority

# Stripe
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_PUBLIC_KEY=pk_live_your_public_key

# Email Service (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=noreply@zeetech.com

# Server Configuration
SERVER_NAME=api.zeetech.com
DEBUG=False
TESTING=False

# CORS Configuration
FRONTEND_URL=https://zeetech.com
ALLOWED_ORIGINS=https://zeetech.com,https://www.zeetech.com

# File Upload
MAX_UPLOAD_SIZE=16777216  # 16MB
UPLOAD_FOLDER=/app/uploads

# Session
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=2592000  # 30 days

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/zeetech_backend.log

# Security
BCRYPT_LOG_ROUNDS=12
```

---

## Security Considerations

### 1. HTTPS/SSL Setup

#### With Certbot (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d api.zeetech.com

# Certificate located at:
# /etc/letsencrypt/live/api.zeetech.com/fullchain.pem
# /etc/letsencrypt/live/api.zeetech.com/privkey.pem

# Auto-renew (runs daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 2. Nginx Configuration

```nginx
# /etc/nginx/sites-available/zeetech

upstream flask_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name api.zeetech.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.zeetech.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.zeetech.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.zeetech.com/privkey.pem;
    
    # SSL security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Logging
    access_log /var/log/nginx/zeetech_access.log;
    error_log /var/log/nginx/zeetech_error.log;
}
```

Enable configuration:

```bash
sudo ln -s /etc/nginx/sites-available/zeetech /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### 3. Rate Limiting

Add to `app/__init__.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

app = create_app()
limiter.init_app(app)

# Apply to routes
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    pass
```

### 4. CORS Configuration

Update `app/__init__.py`:

```python
CORS(app, 
     origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

### 5. Database Security

```python
# In config.py - Use connection string with authentication
class ProductionConfig(Config):
    # MongoDB with authentication
    MONGODB_URI = os.getenv('MONGODB_URI', 
        'mongodb+srv://user:password@cluster.mongodb.net/zeetech')
    
    # Disable debug
    DEBUG = False
    TESTING = False
    
    # Secure session cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
```

---

## Monitoring & Logging

### 1. Application Logging

Logs are written to `logs/zeetech_backend.log` with rotation:

```bash
# View recent logs
tail -f logs/zeetech_backend.log

# Filter errors
grep ERROR logs/zeetech_backend.log

# Count requests
grep "REQUEST:" logs/zeetech_backend.log | wc -l
```

### 2. Systemd Service

Create `/etc/systemd/system/zeetech-backend.service`:

```ini
[Unit]
Description=ZeeTech Flask Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/zeetech_backend
ExecStart=/var/www/zeetech_backend/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start zeetech-backend
sudo systemctl enable zeetech-backend
sudo systemctl status zeetech-backend
```

### 3. Health Checks

```bash
# Docker health check
curl http://localhost:5000/health

# Monitor endpoint
curl http://api.zeetech.com/api/admin/stats  # For admins only
```

### 4. Backup Strategy

```bash
#!/bin/bash
# backup.sh - Run daily via cron

BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/zeetech_$DATE.dump"

# Create backup
mongodump --uri="mongodb+srv://user:pass@cluster/zeetech" \
          --out="$BACKUP_FILE"

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

# Upload to cloud storage (S3, GCS, etc.)
aws s3 cp "$BACKUP_FILE" s3://backups/zeetech/
```

Cron entry:

```
0 2 * * * /home/ubuntu/backup.sh
```

---

## Troubleshooting

### Cannot Connect to MongoDB

```bash
# Check MongoDB is running
mongosh

# Verify connection string format
# mongodb+srv://user:password@cluster/database

# Test connection
python -c "from pymongo import MongoClient; \
    client = MongoClient('db_uri'); \
    print(client.server_info())"
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
gunicorn --bind 0.0.0.0:8000 run:app
```

### Stripe Webhook Not Working

```python
# Verify webhook configuration
1. Go to Stripe Dashboard → Webhooks
2. Check endpoint URL: https://api.zeetech.com/api/payments/webhook
3. Verify signing secret is in .env as STRIPE_WEBHOOK_SECRET
4. Test webhook delivery in dashboard
```

### High Memory Usage

```bash
# Check running processes
ps aux | grep python

# Limit workers
gunicorn --workers 2 run:app

# Monitor memory
watch -n 1 free -m
```

### Slow Queries

```bash
# Enable MongoDB query profiling
db.setProfilingLevel(1)

# Check slow queries
db.system.profile.find().sort({ ts: -1 }).limit(10)
```

---

## Deployment Checklist

- [ ] All environment variables set
- [ ] Database migrations completed
- [ ] SSL certificate installed
- [ ] Email service configured
- [ ] Stripe keys set to production
- [ ] CORS configured for production domain
- [ ] Logging configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Rate limiting configured
- [ ] Tests passing on production environment
- [ ] Rollback plan documented

For additional help or issues, refer to the [README.md](README.md) or contact the development team.
