# 🚀 Quick Start Guide - Zeetech Project

## What Was Fixed

✅ **API Base URL** - Removed leading space and changed IP to localhost  
✅ **Markdown Linting** - Fixed code blocks, tables, and headings  
✅ **Flask Backend** - Verified running successfully on localhost:5000  

---

## 🚀 Quick Start (< 5 minutes)

### Terminal 1: Start Backend

```bash
cd flask_backend
pip install -r requirements.txt
python run.py
```

**Expected:** `Running on http://127.0.0.1:5000`

### Terminal 2: Start Frontend

```bash
cd zeetech
flutter pub get
flutter run -d web
```

**Expected:** `Serving on http://localhost:8080`

---

## ✅ Verify It Works

### Check Backend
```bash
# In a new terminal:
curl http://localhost:5000/api/health
# Should respond with: {"status":"ok"}
```

### Check Frontend
- Open http://localhost:8080 in browser
- Press F12 to open DevTools
- Go to Network tab
- Try logging in
- You should see API requests to http://localhost:5000/api/

---

## 🔧 Key Configuration

| Setting | Value | File |
|---------|-------|------|
| Frontend URL | http://localhost:8080 | automatic (Flutter) |
| Backend URL | http://localhost:5000 | `zeetech/lib/core/constants/app_constants.dart` |
| API Base | http://localhost:5000/api | `app_constants.dart` (line 11) |

---

## 📋 Troubleshooting

### "Connection Refused"
- Is backend running? (Terminal 1)
- Is port 5000 free? `netstat -ano | findstr :5000`

### "Port Already in Use"
```bash
# Find what's using port 5000
netstat -ano | findstr :5000
# Kill the process
taskkill /PID <PID> /F
```

### "API Request Failed"
- Check DevTools Network tab (F12)
- Look for errors in Console tab
- Verify backend is running

---

## 🧪 Test Authentication

1. Open http://localhost:8080
2. Navigate to Signup/Login
3. Try creating an account
4. Watch Network tab for API calls
5. Check for success messages

---

## 📚 Full Documentation

See [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) for detailed information.

---

## 🎯 Next Steps

1. ✅ Both services running
2. ⏳ Test user registration
3. ⏳ Test booking flow
4. ⏳ Verify Supabase integration
5. ⏳ Deploy to production

---

**All Systems Go! 🎉**
