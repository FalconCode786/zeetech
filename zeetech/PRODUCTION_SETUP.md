# Zeetech - Production-Ready Setup Guide

## Overview

This document provides comprehensive setup and deployment instructions for the Zeetech Flutter application, which has been configured for production readiness.

## ✅ Production Improvements Implemented

### 1. **Environment Configuration System**
- Multi-environment support (Development, Staging, Production)
- Centralized configuration management
- Easy switching between API endpoints

### 2. **Secure Storage & Initialization**
- Proper initialization sequence in `main()` before app startup
- Null-safe storage service with validation
- Secure token handling with refresh token support

### 3. **Advanced Error Handling**
- Structured exception hierarchy (ApiException, NetworkException, etc.)
- Global error boundary widget for uncaught exceptions
- Proper error page with stack traces (in debug mode)

### 4. **Network Resilience**
- Automatic retry with exponential backoff (configurable)
- Timeout handling
- Connection error recovery
- Token refresh mechanism with queued requests

### 5. **Input Validation**
- Email, phone, password validation with proper regex
- Full name and address validation
- Secure password requirements enforcement
- Input sanitization

### 6. **Structured Logging**
- Production-safe logging (no sensitive data exposed)
- Configurable log levels
- Crash reporting ready (integrate Crashlytics/Sentry)
- Debug vs Production differentiation

### 7. **Data Safety**
- Safe JSON parsing in models with type validation
- Default value fallbacks
- Comprehensive error logging
- Equality/hashCode implementation for models

### 8. **Authentication Flow**
- Proper initialization synchronization
- Token refresh before expiry
- Graceful logout on auth failure
- Input validation before API calls

---

## 🚀 Environment Setup

### For **Development** (Android Emulator/iOS Simulator)

```dart
// Build with development environment
AppEnvironment.setEnvironment(Environment.development);

// API URLs:
// Android Emulator: http://10.0.2.2:5000/api
// iOS Simulator:    http://localhost:5000/api  
// Physical Device:  http://192.168.x.x:5000/api (update IP)
```

**Run commands:**
```bash
# Development build (Android Emulator)
flutter run

# Development build (Physical Device - update API IP)
flutter run --release
```

### For **Staging** (Testing with staging server)

```dart
// automatic in AppEnvironment class
AppEnvironment.setEnvironment(Environment.staging);
// Uses: https://staging-api.zeetech.com/api
```

**Run commands:**
```bash
flutter run --dart-define=ENVIRONMENT=staging
```

### For **Production** (Release build)

```dart
AppEnvironment.setEnvironment(Environment.production);
// Uses: https://api.zeetech.com/api
```

**Run commands:**
```bash
# Build Android APK
flutter build apk --release

# Build Android App Bundle (for Play Store)
flutter build appbundle --release

# Build iOS
flutter build ios --release
```

---

## 🔧  Configuration Files

### Key Configuration Classes

**`lib/core/config/environment.dart`**
- Environment selection (dev/staging/prod)
- API base URLs
- Timeout configurations
- Retry strategy parameters
- Logging behavior

**`lib/core/utils/app_logger.dart`**
- Structured logging with levels
- Sensitive data redaction
- Integration points for crash reporting
- Debug vs production differentiation

**`lib/core/utils/validation_utils.dart`**
- Input validation regexes
- Error message handling
- Data sanitization

---

## 🔐 Security Checklist

### Before Production Release

- [ ] Ensure HTTPS is used for all API endpoints (not HTTP)
- [ ] Verify API base URL is correctly set to production
- [ ] Check that `AppEnvironment.isProduction` returns true
- [ ] Enable crash reporting (Firebase Crashlytics/Sentry)
- [ ] Configure API rate limiting on backend
- [ ] Set proper CORS headers on backend
- [ ] Remove all debug logs from API responses
- [ ] Verify token refresh mechanism works
- [ ] Test force update mechanism
- [ ] Review authentication flow for security

### API Security

```dart
// Token automatically added to all requests
// Authorization: Bearer <token>

// Token refresh happens automatically on 401
// Old requests are retried after token refresh

// Sensitive data is redacted from logs
AppLogger.debug('Request data: $sensitiveData'); // Shows ***REDACTED***
```

---

## 📋 Initialization Sequence

The app initializes in this critical order:

1. **Flutter bindings** - `WidgetsFlutterBinding.ensureInitialized()`
2. **Environment setup** - `AppEnvironment.setEnvironment()`
3. **Storage initialization** - `StorageService().init()` ⚠️ CRITICAL
4. **API service initialization** - `ApiService().initialize()`
5. **Error handlers** - Global error catching
6. **App launch** - `runApp()`

**If StorageService is not initialized, the app will crash on first token access!**

---

## 🧪 Testing the Setup

### Test Error Handling

```dart
// Navigate to any screen and throw an error
throw Exception('Test error - should see error dialog');

// The error boundary will catch it and display gracefully
```

### Test Network Retry

```dart
// Turn off wifi and trigger an API call
// Should retry with exponential backoff
// Max retries: 3 (dev), configurable in AppEnvironment
```

### Test Token Refresh

1. Login (token stored securely)
2. Let token expire (modify StorageService to expire token)
3. Trigger API call
4. Should automatically refresh token and retry request

### Test Input Validation

```dart
// Try invalid inputs in registration/login
// - Email: "invalid"
// - Phone: "123"  
// - Password: "weak"
// - Name: "A"

// Should show validation error messages
```

---

## 🐛 Debugging

### Enable Debug Logging

```dart
// Already enabled in development environment
// Check: AppEnvironment.enableLogging

// Logs appear in: terminal/console
// Format: [DEBUG] [ISO_TIMESTAMP] message
```

### Check Logs

```bash
# Flutter logs
flutter logs

# Filter specific tags
flutter logs | grep "ApiService"
flutter logs | grep ERROR
```

### Monitor StorageService

```dart
// Check if initialized
if (!StorageService().isInitialized) {
  print('Storage not ready!');
}

// View stored user data
final user = await StorageService().getUser();
print(user);
```

---

## 📦 Build & Deployment

### Android

```bash
# Release build
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk

# App Bundle for Play Store
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab

# Sign APK (already configured in android/build.gradle.kts)
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
  -keystore ~/key.jks build/app/outputs/flutter-apk/app-release.apk key0
```

### iOS

```bash
# Release build
flutter build ios --release

# Build and sign
cd ios
xcodebuild -workspace Runner.xcworkspace -scheme Runner \
  -configuration Release -derivedDataPath build -arch arm64 \
  -allowProvisioningUpdates
```

---

## 🔄 API Integration

### Successful Response

```json
{
  "data": { ... },
  "message": "Success",
  "status_code": 200
}
```

### Error Response

```json
{
  "error": "Invalid credentials",
  "status_code": 401
}
```

### Retry Logic

```
Request → Fail (retryable error)
  ↓
Wait (exponential backoff)
  ↓
Retry (max 3 times in production)
  ↓
Success → Return
Failure → Show user error
```

---

## 📞 Support

For issues:

1. Check logs: `flutter logs`
2. Review error messages in app
3. Verify API server is running
4. Confirm network connection
5. Check environment configuration
6. Review validation error messages

---

## 📝 Changelog

### Version 1.0.0 - Production Ready

**Added:**
- Environment configuration system
- Proper storage initialization
- Advanced error handling
- Network retry mechanism
- Input validation utilities
- Structured logging
- Global error boundary
- Token refresh mechanism
- Safe model parsing

**Fixed:**
- StorageService null pointer crashes
- Hardcoded API URLs
- Missing token refresh logic
- Weak input validation
- Unsafe JSON parsing
- Debug prints in production
- Authentication race conditions

---

## 🎯 Next Steps

1. **Update API URLs** - Change staging/production URLs to your server
2. **Add Crash Reporting** - Integrate Firebase Crashlytics or Sentry
3. **Implement Analytics** - Add event tracking
4. **Add Unit Tests** - Create tests for validators and models
5. **Add Widget Tests** - Test UI components
6. **Configure CI/CD** - Setup automated builds

---

For more information, contact: support@zeetech.com
