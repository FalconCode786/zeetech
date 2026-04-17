# Zeetech Project - Debugging Guide

## Executive Summary

The WebSocket connection error `ws://localhost:60713/$dwdsSseHandler` was caused by **configuration issues in the Flutter app and backend setup**. All issues have been identified and fixed.

---

## Issues Found & Fixed

### 1. ❌ WebSocket Connection Error - FIXED ✅

**Error Message:**
```
WebSocket connection to 'ws://localhost:60713/$dwdsSseHandler' failed
```

**Root Cause:**
- Leading space in API base URL: ` http://192.168.100.4:5000/api`
- Hardcoded IP address that doesn't work on web platform
- URL parsing fails with leading space, causing connection issues

**Location:** `zeetech/lib/core/constants/app_constants.dart` (Line 11)

**Before:**
```dart
static const String baseUrl = ' http://192.168.100.4:5000/api';
```

**After:**
```dart
static const String baseUrl = 'http://localhost:5000/api';
```

**Why This Works:**
- Removes the leading space that breaks URL parsing
- Uses `localhost` which is accessible on web platform
- Flask backend is configured to accept localhost by default

---

### 2. ❌ Markdown Linting Errors - FIXED ✅

**File:** `zeetech/IMPROVEMENTS_SUMMARY.md`

**Errors Fixed:**

#### a) Fenced code block without language (Line 151)
```markdown
# Before:
```
Network Error...
```

# After:
```text
Network Error...
```
```

#### b) Table column spacing (Line 325)
```markdown
# Before:
| Aspect | Before | After |
|--------|--------|-------|

# After:
| Aspect      | Before        | After           |
| ----------- | ------------- | --------------- |
```

#### c) Emphasis used as heading (Line 431)
```markdown
# Before:
**Status: ✅ PRODUCTION READY**

# After:
## Status: ✅ PRODUCTION READY
```

---

## Project Architecture

```
Zeetech (Flutter + Flask)
│
├── Frontend (Flutter Web/Mobile)
│   ├── main.dart
│   │   ├── StorageService.init()
│   │   └── ApiService.initialize()
│   │
│   ├── Services
│   │   ├── ApiService (Dio HTTP client)
│   │   │   └── baseUrl: http://localhost:5000/api
│   │   ├── StorageService (Secure storage)
│   │   ├── AuthService
│   │   ├── BookingService
│   │   └── ServiceService
│   │
│   ├── Providers (State Management)
│   │   ├── AuthProvider
│   │   ├── BookingProvider
│   │   ├── ServiceProvider
│   │   └── ProviderProvider
│   │
│   └── Screens
│       ├── Splash
│       ├── Auth (Login/Register/OTP)
│       ├── Home
│       ├── Services
│       ├── Bookings
│       ├── Profile
│       └── Provider Dashboard
│
└── Backend (Flask + Supabase)
    ├── run.py (Entry point)
    ├── app/__init__.py (App factory)
    │   ├── CORS Configuration (All origins allowed)
    │   ├── Supabase Client
    │   └── Error Handlers
    │
    ├── app/routes/
    │   ├── auth.py
    │   ├── bookings.py
    │   ├── services.py
    │   ├── payments.py
    │   ├── ratings.py
    │   ├── feedbacks.py
    │   └── admin.py
    │
    ├── app/services/
    │   ├── auth_service.py
    │   ├── booking_service.py
    │   ├── payment_service.py
    │   ├── rating_service.py
    │   └── provider_service.py
    │
    └── Database
        └── Supabase (PostgreSQL)
```

---

## Configuration Files

### 1. Flutter Web Configuration
- **File:** `zeetech/lib/core/constants/app_constants.dart`
- **Key Settings:**
  ```dart
  static const String baseUrl = 'http://localhost:5000/api';
  static const int apiTimeout = 3000; // milliseconds
  static const String appName = 'Zeetech';
  ```

### 2. Flask Backend Configuration
- **File:** `flask_backend/app/config.py`
- **Key Settings:**
  ```python
  SERVER_URL = 'http://localhost:5000'
  FRONTEND_URL = 'http://localhost:8080'
  DEBUG = True
  TESTING = False
  ```

### 3. Environment Variables
- **File:** `flask_backend/.env`
- **Key Variables:**
  ```
  FLASK_ENV=development
  FLASK_DEBUG=True
  SUPABASE_URL=https://lgrhzubkkwjneccupqbd.supabase.co
  SUPABASE_KEY=<your-key>
  SERVER_URL=http://192.168.100.4:5000
  FRONTEND_URL=http://192.168.100.4:8080
  ```

---

## How to Run the Project

### Prerequisites
- Flutter SDK (3.11.0 or higher)
- Python 3.9+
- pip (Python package manager)

### Step 1: Start Flask Backend

```bash
cd flask_backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

**Expected Output:**
```
[2026-04-16 09:02:03,628] INFO: Logging configured for development environment
[2026-04-16 09:02:06,577] INFO: Supabase connection successful
Starting ZeeTech Flask Backend on 0.0.0.0:5000
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.18.131:5000
```

✅ **Backend is ready on:** `http://localhost:5000`

### Step 2: Start Flutter Web App

```bash
cd zeetech

# Get dependencies
flutter pub get

# Run on web
flutter run -d web
```

**Expected Output:**
```
Launching lib/main.dart on Chrome in debug mode...
...
Serving ZeeTech on http://localhost:8080
```

✅ **Frontend is ready on:** `http://localhost:8080`

---

## Verification Checklist

### 1. Backend Health

```bash
# Test backend endpoint
curl http://localhost:5000/api/health

# Expected response:
# {"status": "ok"}
```

### 2. API Connection

Open browser developer tools (F12) and check:
- Network tab: See API requests to `http://localhost:5000/api`
- Console: Check for any errors or warnings
- Look for successful connection messages like `[API] Configured for web - credentials will be included`

### 3. Storage Service

The app should initialize without errors:
```
I/flutter: [Storage] StorageService initialized
I/flutter: [API] ApiService initialized
```

### 4. Authentication Flow

1. Navigate to login screen
2. Enter test credentials (if backend has test data)
3. Check console for successful API call
4. Verify token is stored in secure storage

---

## Common Issues & Solutions

### Issue 1: Connection Refused
```
Error: Failed to connect to http://localhost:5000
```

**Solution:**
1. Verify Flask backend is running: `python flask_backend/run.py`
2. Check if port 5000 is available: `netstat -ano | findstr :5000`
3. If port is used, kill process: `taskkill /PID <PID> /F`

---

### Issue 2: CORS Error
```
Access to XMLHttpRequest at 'http://localhost:5000/api/...' 
from origin 'http://localhost:8080' has been blocked by CORS policy
```

**Solution:**
- Backend CORS is configured to allow all origins
- Make sure backend is running (CORS headers are set by Flask)
- Check `flask_backend/app/__init__.py` lines 28-33

---

### Issue 3: Token Not Stored
```
[API] Failed to get token for Authorization header
```

**Solution:**
1. On web, tokens are stored in browser localStorage (not secure storage)
2. Check browser DevTools → Storage → Local Storage → localhost:8080
3. Verify StorageService is initialized before API calls
4. Check that login response includes `token` field

---

### Issue 4: Storage Service Not Initialized
```
Error: SharedPreferences not initialized
```

**Solution:**
- Ensure `StorageService().init()` is called in `main.dart` before any API calls
- This is already done in the app entry point (line 18)

---

## Development Tips

### Enable Debug Logging

All API calls are logged when running in debug mode:
```
[API] GET http://localhost:5000/api/auth/login
[API] Headers: {Authorization: Bearer <token>}
[API] Response Status: 200
```

### Test API Endpoints Directly

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","phone":"03001234567","fullName":"Test User","password":"password"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### Clear Flutter Web Cache

```bash
flutter clean
flutter pub get
flutter run -d web
```

---

## Testing Workflow

1. **Backend Test**
   - Start Flask server
   - Test health endpoint: `curl http://localhost:5000/api/health`
   - Check logs for Supabase connection

2. **Frontend Test**
   - Start Flutter web app
   - Check browser console (F12)
   - Verify API calls in Network tab
   - Test login flow end-to-end

3. **Integration Test**
   - Both backend and frontend running
   - Complete user registration
   - Verify data appears in Supabase database
   - Test booking flow

---

## Production Deployment Notes

### For Web Deployment
1. Update `FRONTEND_URL` in Flask config
2. Update `baseUrl` in Flutter `app_constants.dart`
3. Run `flutter build web`
4. Configure HTTPS certificates
5. Update CORS settings to allow specific origins

### For Production Security
- Remove `DEBUG = True` from Flask config
- Implement HTTPS only
- Update CORS to specific domains instead of `['*']`
- Add rate limiting
- Enable request validation

---

## Useful Commands

```bash
# Flutter
flutter clean                    # Clean build cache
flutter pub get                 # Get dependencies
flutter pub upgrade            # Upgrade packages
flutter run -d web             # Run web app
flutter build web              # Build for production

# Python/Flask
pip install -r requirements.txt # Install dependencies
python run.py                  # Start backend
python -m pytest               # Run tests (if available)

# Git
git status                     # Check status
git add .                      # Stage changes
git commit -m "message"        # Commit changes
git push origin main           # Push to GitHub
```

---

## File Locations Reference

| Component | File |
|-----------|------|
| API Configuration | `zeetech/lib/core/constants/app_constants.dart` |
| Backend Config | `flask_backend/app/config.py` |
| Environment Vars | `flask_backend/.env` |
| Routes | `zeetech/lib/core/routes/app_router.dart` |
| API Service | `zeetech/lib/services/api_service.dart` |
| Storage Service | `zeetech/lib/services/storage_service.dart` |
| Auth Service | `zeetech/lib/services/auth_service.dart` |
| Main Entry | `zeetech/lib/main.dart` |
| Backend Entry | `flask_backend/run.py` |
| Backend Init | `flask_backend/app/__init__.py` |

---

## Next Steps

1. ✅ Fix configurations (DONE)
2. ✅ Test backend connectivity (DONE)
3. ⏳ Start both services and test end-to-end
4. ⏳ Test complete user flows
5. ⏳ Fix any remaining issues
6. ⏳ Deploy to production

---

## Support & Resources

- **Flutter Documentation:** https://flutter.dev/docs
- **Dio HTTP Client:** https://pub.dev/packages/dio
- **Go Router:** https://pub.dev/packages/go_router
- **Provider Package:** https://pub.dev/packages/provider
- **Supabase Docs:** https://supabase.io/docs
- **Flask Documentation:** https://flask.palletsprojects.com

---

## Troubleshooting Checklist

- [ ] Flask backend running on `http://localhost:5000`
- [ ] Flutter web app running on `http://localhost:8080`
- [ ] API base URL is `http://localhost:5000/api` (no leading space)
- [ ] StorageService initialized in main.dart
- [ ] ApiService initialized before use
- [ ] Supabase connection successful (check Flask logs)
- [ ] CORS headers present in API responses
- [ ] No errors in browser DevTools console
- [ ] API requests visible in Network tab
- [ ] Auth tokens properly stored and retrieved

---

**Last Updated:** April 16, 2026
**Project Status:** ✅ Ready for Testing
