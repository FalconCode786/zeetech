# ZeeTech Flask Backend - Troubleshooting Guide

Common issues and solutions for development and production.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Database Connection](#database-connection)
- [Authentication Issues](#authentication-issues)
- [API Response Issues](#api-response-issues)
- [Payment Integration](#payment-integration)
- [File Upload Issues](#file-upload-issues)
- [Performance Issues](#performance-issues)
- [Production Issues](#production-issues)

---

## Installation Issues

### Issue: ModuleNotFoundError after `pip install -r requirements.txt`

**Symptoms:**

```
ModuleNotFoundError: No module named 'flask'
```

**Solutions:**

1. **Verify virtual environment is activated:**

   ```bash
   # Linux/Mac
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

   Look for `(venv)` prefix in terminal.

2. **Reinstall requirements:**

   ```bash
   pip install --upgrade pip
   pip cache purge
   pip install -r requirements.txt
   ```

3. **Check Python version:**

   ```bash
   python --version  # Should be 3.8+
   ```

---

### Issue: Permission Denied on Linux/Mac

**Symptoms:**

```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

```bash
# Give permissions to project directory
chmod -R 755 flask_backend

# Or use sudo (not recommended for development)
sudo pip install -r requirements.txt
```

---

## Database Connection

### Issue: Cannot Connect to MongoDB

**Symptoms:**

```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused
```

**Diagnostics:**

1. **Check if MongoDB is running:**

   ```bash
   # Linux/Mac
   brew services list | grep mongodb
   
   # Windows (check Services)
   sc query MongoDB
   
   # Docker
   docker ps | grep mongo
   ```

2. **Check connection string:**

   ```bash
   # Local
   MONGODB_URI=mongodb://localhost:27017/zeetech
   
   # Atlas
   MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/zeetech
   ```

**Solutions:**

1. **Start MongoDB locally:**

   ```bash
   # macOS with Homebrew
   brew services start mongodb-community
   
   # Linux with systemd
   sudo systemctl start mongod
   
   # Docker
   docker run -d -p 27017:27017 mongo:6.0
   ```

2. **Test connection:**

   ```python
   from pymongo import MongoClient
   
   uri = "mongodb://localhost:27017"
   client = MongoClient(uri)
   print(client.server_info())
   ```

3. **Verify credentials (MongoDB Atlas):**
   - Go to MongoDB Atlas dashboard
   - Check username/password in connection string
   - Verify IP whitelist includes your IP
   - Test connection: `mongosh "mongodb+srv://user:pass@cluster..."`

---

### Issue: "authentication failed" with MongoDB Atlas

**Symptoms:**

```
pymongo.errors.OperationFailure: authentication failed
```

**Solutions:**

1. **Escape special characters in password:**

   ```
   If password is: p@ssw0rd!123
   URL encode to: p%40ssw0rd%21123
   MONGODB_URI: mongodb+srv://user:p%40ssw0rd%21123@cluster...
   ```

2. **Verify database user:**
   - Atlas Dashboard → Database Access
   - Check user has password set correctly
   - Check user has role "readWrite any database"

3. **Verify connection string format:**

   ```
   # Correct
   mongodb+srv://user:password@cluster.mongodb.net/zeetech?retryWrites=true
   
   # Incorrect
   mongodb://user:password@cluster.mongodb.net/zeetech
   # Missing 'srv' - used for Atlas clusters
   ```

---

### Issue: Connection Timeout

**Symptoms:**

```
ServerSelectionTimeoutError: connection closed
```

**Solutions:**

1. **Check network connectivity:**

   ```bash
   ping database-server.com
   ```

2. **Increase timeout in code:**

   ```python
   from pymongo import MongoClient
   
   client = MongoClient(
       uri,
       serverSelectionTimeoutMS=5000,  # 5 seconds
       connectTimeoutMS=10000,
       socketTimeoutMS=5000
   )
   ```

3. **Check firewall/network:**
   - MongoDB Atlas: Verify IP whitelist
   - Self-hosted: Check firewall rules `sudo ufw allow 27017`
   - Check ISP isn't blocking port 27017

---

## Authentication Issues

### Issue: Login Always Fails

**Symptoms:**

```
UnauthorizedError: Invalid credentials
```

**Check:**

1. **Verify user exists in database:**

   ```bash
   mongosh
   > use zeetech
   > db.users.findOne({ email: "test@example.com" })
   ```

2. **Check password hashing:**

   ```python
   from werkzeug.security import check_password_hash, generate_password_hash
   
   hashed = generate_password_hash("test123")
   print(check_password_hash(hashed, "test123"))  # Should be True
   ```

3. **Test login endpoint:**

   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "test123"
     }' \
     -c cookies.txt
   ```

---

### Issue: Session Expires Too Quickly

**Symptoms:**
User gets logged out unexpectedly.

**Solutions:**

1. **Update session timeout in `.env`:**

   ```bash
   PERMANENT_SESSION_LIFETIME=2592000  # 30 days in seconds
   ```

2. **Enable persistent sessions:**

   ```python
   @app.route('/api/auth/login', methods=['POST'])
   def login():
       user = User.find_by_email(email)
       session.permanent = True
       login_user(user, remember=True)
       return success_response(user.to_dict())
   ```

3. **Check browser settings:**
   - Ensure cookies are not being blocked
   - Check if "Delete cookies on exit" is enabled
   - Clear browser cache/cookies

---

### Issue: "CSRF Token Missing"

**Symptoms:**

```json
{
  "error": "The CSRF token is missing",
  "code": "CSRF_TOKEN_REQUIRED"
}
```

**Solution:**

This app uses session-based auth (no CSRF protection by default). If you see this:

1. **Disable CSRF in development (if using Flask-WTF):**

   ```python
   app.config['WTF_CSRF_ENABLED'] = False  # Only for development
   ```

2. **Or implement proper CSRF handling:**

   ```python
   from flask_wtf.csrf import CSRFProtect
   
   csrf = CSRFProtect(app)
   
   # Client must include X-CSRFToken header from meta tag
   ```

---

## API Response Issues

### Issue: CORS Error in Browser

**Symptoms:**

```
Access to XMLHttpRequest from origin 'http://localhost:3000' 
has been blocked by CORS policy.
```

**Solutions:**

1. **Verify CORS is configured:**
   Check `app/__init__.py`:

   ```python
   CORS(app, 
        origins=['http://localhost:3000'],
        supports_credentials=True)
   ```

2. **Update allowed origins:**

   ```bash
   # .env
   FRONTEND_URL=http://localhost:3000
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

3. **Include credentials in fetch requests:**

   ```javascript
   fetch('http://localhost:5000/api/auth/login', {
     method: 'POST',
     credentials: 'include',  // Important!
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(data)
   })
   ```

---

### Issue: 404 Not Found

**Symptoms:**

```json
{
  "error": "Endpoint not found",
  "code": "NOT_FOUND"
}
```

**Check:**

1. **Verify endpoint URL:**

   ```bash
   # Check route was registered
   curl -X GET http://localhost:5000/api/auth/verify -H "Cookie: session=..."
   
   # Not /api/auth//verify (double slash)
   # Not /API/AUTH/VERIFY (case sensitive)
   ```

2. **List all registered routes:**

   ```python
   # In Flask shell
   from flask import current_app
   for rule in current_app.url_map.iter_rules():
       print(f"{rule.rule} -> {rule.endpoint}")
   ```

3. **Check if blueprint is registered:**
   Look in `app/routes/__init__.py` - all blueprints should be registered:

   ```python
   from .auth import auth_bp
   app.register_blueprint(auth_bp, url_prefix='/api/auth')
   ```

---

### Issue: 400 Bad Request

**Symptoms:**

```json
{
  "error": "Invalid request",
  "code": "INVALID_REQUEST"
}
```

**Solutions:**

1. **Check request body is JSON:**

   ```bash
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \  # Important!
     -d '{"email":"test@test.com","password":"test123"}'
   ```

2. **Validate required fields:**

   ```bash
   # Missing 'password'
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com"}'
   # Returns 422 Validation Error
   ```

3. **Check data types:**

   ```python
   # Wrong: baseAmount as string
   {"baseAmount": "100"}
   # Correct: baseAmount as number
   {"baseAmount": 100}
   ```

---

### Issue: 500 Internal Server Error

**Symptoms:**

```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR"
}
```

**Diagnostics:**

1. **Check application logs:**

   ```bash
   tail -f logs/zeetech_backend.log
   ```

2. **Run in debug mode:**

   ```bash
   FLASK_ENV=development FLASK_DEBUG=1 python run.py
   ```

3. **Get detailed error:**
   Add try-catch with logging:

   ```python
   @app.route('/api/test')
   def test():
       try:
           result = risky_operation()
           return success_response(result)
       except Exception as e:
           current_app.logger.error(f"Error: {str(e)}", exc_info=True)
           raise InternalError(f"Error details: {str(e)}")
   ```

---

## Payment Integration

### Issue: Stripe API Key Invalid

**Symptoms:**

```
stripe.error.AuthenticationError: Invalid API Key provided
```

**Solutions:**

1. **Verify Stripe key format:**

   ```bash
   # Correct format (test key)
   sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Not truncated or with spaces
   STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

2. **Use test vs. production keys:**

   ```bash
   # Development/Testing
   STRIPE_SECRET_KEY=sk_test_xxxxx
   STRIPE_PUBLIC_KEY=pk_test_xxxxx
   
   # Production
   STRIPE_SECRET_KEY=sk_live_xxxxx
   STRIPE_PUBLIC_KEY=pk_live_xxxxx
   ```

3. **Reload environment after changing .env:**

   ```bash
   kill $(lsof -t -i:5000)
   python run.py
   ```

---

### Issue: Webhook Not Receiving Events

**Symptoms:**
Payment succeeds in Stripe but booking not updated in database.

**Solutions:**

1. **Verify webhook endpoint:**

   ```bash
   # Should be accessible publicly
   curl -X POST http://api.zeetech.com/api/payments/webhook \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

2. **Check webhook signing:**

   ```python
   # Stripe Dashboard → Webhooks → Select endpoint → Recent deliveries
   # Test delivery successfully?
   
   # Verify webhook secret in .env
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

3. **Monitor webhook deliveries:**

   ```bash
   # Check logs for webhook processing
   grep "webhook" logs/zeetech_backend.log
   
   # Stripe Dashboard shows delivery status
   # Check retry count and response code
   ```

4. **Test webhook locally:**

   ```bash
   # Use ngrok to expose local server
   ngrok http 5000
   
   # Add ngrok URL to Stripe webhooks
   # https://xxxxxx.ngrok.io/api/payments/webhook
   
   # Use Stripe CLI for testing
   stripe listen --forward-to localhost:5000/api/payments/webhook
   stripe trigger payment_intent.succeeded
   ```

---

##

 File Upload Issues

### Issue: "File type not allowed"

**Symptoms:**

```json
{
  "error": "File type not allowed. Allowed: png, jpg, jpeg, gif, webp",
  "code": "INVALID_FILE_TYPE"
}
```

**Solutions:**

1. **Check allowed extensions in `app/routes/uploads.py`:**

   ```python
   ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
   ```

2. **Verify file has correct extension:**
   - Rename `image.PNG` to `image.png` (lowercase)
   - Don't upload `image.txt` with `.jpg` extension

3. **Add more extensions:**

   ```python
   ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}
   ```

---

### Issue: "File too large"

**Symptoms:**

```json
{
  "error": "File size exceeds maximum allowed size",
  "code": "FILE_TOO_LARGE"
}
```

**Solutions:**

1. **Check size limit in `.env`:**

   ```bash
   MAX_UPLOAD_SIZE=16777216  # 16MB in bytes
   ```

2. **Increase limit if needed:**

   ```bash
   # 50MB
   MAX_UPLOAD_SIZE=52428800
   ```

3. **Compress image before upload:**

   ```python
   from PIL import Image
   
   img = Image.open('large_image.jpg')
   img.thumbnail((1200, 1200))
   img.save('compressed.jpg', optimize=True, quality=85)
   ```

---

### Issue: File Saved But URL Not Returned

**Symptoms:**

```json
{
  "message": "File uploaded successfully",
  "data": {
    "url": null,
    "filename": "xyz.jpg"
  }
}
```

**Solutions:**

1. **Check upload directory exists:**

   ```bash
   mkdir -p /app/uploads
   chmod 755 /app/uploads
   ```

2. **Verify Flask can write to directory:**

   ```python
   import os
   print(os.access('/app/uploads', os.W_OK))
   ```

3. **Check path in config:**

   ```bash
   UPLOAD_FOLDER=/app/uploads
   # Not /home/user/uploads or relative paths
   ```

---

## Performance Issues

### Issue: Slow API Responses

**Symptoms:**
Requests take 5+ seconds to respond.

**Diagnostics:**

1. **Check database queries:**

   ```bash
   # MongoDB profiling
   mongosh
   > use zeetech
   > db.setProfilingLevel(1, { slowms: 100 })
   > db.system.profile.find().sort({ ts: -1 }).limit(5)
   ```

2. **Add timing to code:**

   ```python
   import time
   
   @app.route('/api/bookings')
   def get_bookings():
       start = time.time()
       bookings = db.bookings.find(...)
       print(f"Query took: {time.time() - start}s")
       return response
   ```

3. **Check if indexes exist:**

   ```bash
   mongosh
   > use zeetech
   > db.bookings.getIndexes()
   # Should show indexes on customerId, status, etc.
   ```

**Solutions:**

1. **Add database indexes:**

   ```python
   # In database.py
   db.bookings.create_index([("customerId", 1)])
   db.bookings.create_index([("status", 1), ("customerId", 1)])
   ```

2. **Use pagination:**

   ```bash
   curl http://localhost:5000/api/bookings?page=1&limit=10
   ```

3. **Cache frequently accessed data:**

   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_categories():
       return db.categories.find()
   ```

---

### Issue: High Memory Usage

**Symptoms:**
Application crashes or server becomes unresponsive.

**Solutions:**

1. **Limit worker count:**

   ```bash
   gunicorn --workers 2 run:app  # Not 4 or 8 on shared hosting
   ```

2. **Limit pagination results:**

   ```python
   # max 100 results per page
   limit = min(int(request.args.get('limit', 10)), 100)
   ```

3. **Close database cursors:**

   ```python
   cursor = db.bookings.find({})
   for booking in cursor:
       process(booking)
   cursor.close()
   ```

---

## Production Issues

### Issue: Application Won't Start After Deployment

**Symptoms:**

```
systemctl status zeetech-backend
# Shows failed or inactive
```

**Solutions:**

1. **Check logs:**

   ```bash
   sudo journalctl -u zeetech-backend -n 50
   ```

2. **Verify environment variables:**

   ```bash
   sudo systemctl cat zeetech-backend | grep Environment
   
   # Add missing variables
   sudo systemctl edit zeetech-backend
   ```

3. **Test manually:**

   ```bash
   cd /var/www/zeetech_backend
   source venv/bin/activate
   python run.py
   # Check for error messages
   ```

---

### Issue: Certificate Validation Error

**Symptoms:**

```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**

1. **Renew certificate:**

   ```bash
   sudo certbot renew --dry-run
   sudo certbot renew
   ```

2. **Check certificate expiration:**

   ```bash
   openssl x509 -in /etc/letsencrypt/live/domain/cert.pem -text -noout | grep -A2 "Validity"
   ```

3. **Update Nginx config:**

   ```bash
   sudo systemctl reload nginx
   ```

---

### Issue: Out of Disk Space

**Symptoms:**

```
IOError: [Errno 28] No space left on device
```

**Solutions:**

1. **Check disk space:**

   ```bash
   df -h
   ```

2. **Clean old logs:**

   ```bash
   # Logs already rotate, but check size
   ls -lh /var/log/nginx/
   sudo rm -rf /var/log/zeetech_backend.log.20*
   ```

3. **Cleanup temporary files:**

   ```bash
   rm -rf /tmp/*
   sudo journalctl --vacuum=time=7d
   ```

4. **Archive old uploads:**

   ```bash
   find /app/uploads -mtime +90 -exec archive {} \;
   ```

---

### Issue: Database Connection Pool Exhausted

**Symptoms:**

```
pymongo.errors.PoolError: No write concern mode named 'acknowledged'
```

**Solutions:**

1. **Increase pool size:**

   ```python
   client = MongoClient(
       uri,
       maxPoolSize=50,
       minPoolSize=10
   )
   ```

2. **Close idle connections:**

   ```python
   # In app context cleanup
   @app.teardown_appcontext
   def close_database(error):
       mongo_client = g.get('mongo_client')
       if mongo_client is not None:
           mongo_client.close()
   ```

---

For additional help, open an issue on GitHub or contact the development team.
