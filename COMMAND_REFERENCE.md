# 🚀 Quick Command Reference - Zeetech Project

## 📋 All-in-One Setup & Run Guide

### First Time Setup

```bash
# 1. Backend Setup
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/backend'
npm install

# 2. Frontend Setup
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'
flutter pub get
```

---

## 🎮 Running Both Services

### Option 1: Manual (Recommended for Development)

**Terminal 1 - Backend:**

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/backend'
npm run dev
# Expected output: ✓ ZeeTech Express Backend started on http://localhost:5000
```

**Terminal 2 - Frontend:**

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'
flutter run -d chrome --web-port 8080
# Expected output: Flutter run key commands available
```

**Access:** Open browser to `http://localhost:8080`

---

### Option 2: Production Build (Web Only)

**Backend:**

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/backend'
npm start
```

**Frontend (Production Build):**

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'
flutter build web
# Then serve the build/web directory with a web server
```

---

## 🔍 Testing & Verification

### Backend Health Check

```bash
# Direct test
curl http://localhost:5000/health

# With formatted output
curl -s http://localhost:5000/health | jq '.'
```

### Frontend Accessibility

```bash
# Check if frontend is serving
curl http://localhost:8080 | grep -i "title"

# Should contain: <title>zeetech</title>
```

### Test Authentication (from browser console F12)

```javascript
// Test registration
fetch('http://localhost:5000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    phone: '03001234567',
    fullName: 'Test User',
    password: 'Password123!',
    role: 'customer'
  })
})
.then(r => r.json())
.then(d => console.log(d))

// Test login
fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'Password123!'
  })
})
.then(r => r.json())
.then(d => console.log(d))
```

---

## 🔧 Backend Commands

### Development

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/backend'

# Start with hot-reload (nodemon)
npm run dev

# Start production mode
npm start

# Run linter
npm run lint

# Run tests
npm test

# Install dependencies
npm install

# Update dependencies
npm update
```

### Troubleshooting Backend

```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process on port 5000 (Windows)
taskkill /PID <PID> /F

# Clear node_modules and reinstall
rm -r node_modules
npm install

# Check npm version
npm --version

# Check Node version
node --version
```

---

## 🎨 Frontend Commands

### Development

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'

# Install dependencies
flutter pub get

# Analyze code for issues
flutter analyze

# Run app on Chrome
flutter run -d chrome --web-port 8080

# Run app on Edge
flutter run -d edge --web-port 8080

# Run app on Windows Desktop
flutter run -d windows
```

### Building

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'

# Web build (release mode)
flutter build web

# Web build (debug mode)
flutter build web --debug

# Check build size
flutter build web --analyze-size
```

### Debugging

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'

# Enable verbose output
flutter run -d chrome -v

# Clear cache before running
flutter clean
flutter pub get
flutter run -d chrome --web-port 8080

# Check Flutter SDK
flutter doctor

# Check dependencies with updates
flutter pub outdated
```

### Hot Reload & Restart

```bash
# In terminal while app is running:
r         # Hot reload (reload code without losing state)
R         # Hot restart (restart app completely)
h         # Show all available commands
d         # Detach from running app
c         # Clear console
q         # Quit app
```

---

## 📊 Monitoring & Logs

### Watch Backend Logs

```bash
# Backend should already show logs when running
# Look for patterns:
# ✓ Supabase initialized successfully
# ✓ ZeeTech Express Backend started
# [timestamp] GET/POST /api/...
```

### Monitor Port Usage

```bash
# Check all ports in use
netstat -ano

# Check specific port
netstat -ano | findstr :5000
netstat -ano | findstr :8080

# Continuous monitoring (Linux/WSL)
watch "netstat -ano | findstr ':5000\|:8080'"
```

### View Browser Logs

```
1. Open app in browser: http://localhost:8080
2. Press F12 to open DevTools
3. Go to Console tab for errors
4. Go to Network tab to see API calls
5. Go to Application → Storage → LocalStorage for stored data
```

---

## 🛠️ Configuration Updates

### Change Backend Port

**File:** `backend/src/config/config.js`

```javascript
port: process.env.PORT || 5000,  // Change 5000 to your port
```

### Change Frontend API URL

**File:** `zeetech/lib/core/constants/app_constants.dart`

```dart
static const String baseUrl = 'http://localhost:5000';  // Change if needed
```

### Change Frontend Web Port

```bash
flutter run -d chrome --web-port 8080  # Change 8080 to your port
```

---

## 🚨 Common Issues & Fixes

### Port Already in Use

```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill it
taskkill /PID <PID> /F

# Or change port
npm run dev PORT=5001
```

### Flutter Dependencies Issue

```bash
# Clear pub cache
flutter pub cache clean

# Get fresh dependencies
flutter clean
flutter pub get
```

### Backend Not Responding

```bash
# Verify backend is running
curl http://localhost:5000/health

# Check .env file exists
ls 'c:/Users/numl-/OneDrive/Desktop/zeetech2/backend/.env'

# Restart backend
npm run dev
```

### Frontend Can't Connect to Backend

```
1. Check backend is running on port 5000
2. Check baseUrl in app_constants.dart
3. Check CORS configuration in backend
4. Open browser DevTools (F12) → Console for errors
5. Check Network tab for API calls and responses
```

---

## 📱 Platform-Specific Commands

### Android Device

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'
flutter run -d <device-id>  # First run: flutter devices
```

### iOS Device

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'
flutter run -d <device-id>  # Requires macOS
```

### Windows Desktop

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'
flutter run -d windows
```

### Web - Different Browsers

```bash
# Chrome
flutter run -d chrome --web-port 8080

# Edge
flutter run -d edge --web-port 8080

# Firefox
flutter run -d firefox --web-port 8080
```

---

## 📦 Dependency Management

### Backend

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/backend'

# Install specific package
npm install <package-name>

# Install dev dependency
npm install --save-dev <package-name>

# Update all packages
npm update

# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix
```

### Frontend

```bash
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'

# Add package
flutter pub add <package_name>

# Add dev dependency
flutter pub add --dev <package_name>

# Remove package
flutter pub remove <package_name>

# Update all packages
flutter pub upgrade

# Get specific version
flutter pub add package_name:^1.0.0
```

---

## 📋 Maintenance Commands

### Regular Checkup

```bash
# Backend health
curl http://localhost:5000/health

# Frontend health
curl http://localhost:8080

# Check dependencies for updates
npm outdated              # Backend
flutter pub outdated      # Frontend

# Run linter
npm run lint              # Backend
flutter analyze           # Frontend
```

### Clean Up

```bash
# Backend
npm cache clean --force
rm -r node_modules
npm install

# Frontend
flutter clean
flutter pub cache clean
flutter pub get
```

### Reset Everything

```bash
# Backend
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/backend'
rm -r node_modules
npm install
npm run dev

# Frontend
cd 'c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech'
flutter clean
flutter pub get
flutter run -d chrome --web-port 8080
```

---

## 🔑 Environment Variables

### Backend (.env)

```env
PORT=5000
NODE_ENV=development
SUPABASE_URL=https://lgrhzubkkwjneccupqbd.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=akTiuCbETFprCMA2Kc9ZOQ...
JWT_SECRET=your-very-secure-secret-key-change-in-production
```

Location: `c:/Users/numl-/OneDrive/Desktop/zeetech2/backend/.env`

---

## 📞 Quick Reference URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend App | <http://localhost:8080> | Main application |
| Backend Health | <http://localhost:5000/health> | Server status |
| API Base | <http://localhost:5000/api> | All API endpoints |
| Browser DevTools | F12 (in browser) | Debugging frontend |
| Flutter DevTools | `flutter pub global activate devtools` then `devtools` | Debugging app |

---

## 💡 Tips & Tricks

### Visual Studio Code Extensions

```
- Flutter
- Dart
- REST Client
- Thunder Client
- JSON Viewer
```

### Testing APIs from VS Code

```
Install REST Client extension, create requests.rest file:
GET http://localhost:5000/health

###

POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "phone": "03001234567",
  "fullName": "Test User",
  "password": "Password123!",
  "role": "customer"
}
```

### Speed Up Flutter Build

```bash
# Use null-safety optimization
flutter run --no-null-assertions

# Skip snapshot build
flutter run --no-build

# Limit target architectures
flutter run --target-platform android-arm
```

---

*Last Updated: April 17, 2026*  
*Version: 1.0*  
*Project: Zeetech Service Booking Platform*
