# ZeeTech Flask Backend - API Documentation

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Authentication](#auth)
  - [Users](#users)
  - [Services](#services)
  - [Bookings](#bookings)
  - [Ratings](#ratings)
  - [Payments](#payments)
  - [Admin](#admin)
  - [Uploads](#uploads)

## Overview

The ZeeTech Flask Backend provides a REST API for a service booking marketplace. All endpoints return JSON responses.

**Base URL:** `http://localhost:5000/api`

**Response Format:**

```json
{
  "message": "Success message",
  "data": {},
  "error": "Error message (if applicable)",
  "code": "ERROR_CODE (if applicable)"
}
```

## Authentication

### Session-Based Authentication

The API uses Flask-Login with secure sessions. After login, a session cookie is stored automatically. Include `"credentials": "include"` in fetch requests to send cookies.

### Error Responses

- **401 Unauthorized:** User not logged in
- **403 Forbidden:** User lacks required permissions
- **422 Unprocessable Entity:** Validation error

## API Endpoints

### Health Check

#### GET /health

Check server status.

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "message": "ZeeTech Backend is running"
}
```

---

## Auth

### POST /api/auth/register

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "phone": "+1234567890",
  "fullName": "John Doe",
  "password": "password123",
  "role": "customer" // or "provider"
}
```

**Response:** `201 Created`

```json
{
  "message": "User registered successfully",
  "data": {
    "user": {
      "_id": "user_id",
      "email": "user@example.com",
      "fullName": "John Doe",
      "role": "customer",
      "status": "active",
      "rating": 0,
      "totalReviews": 0,
      "createdAt": "2026-04-11T10:00:00"
    }
  }
}
```

**Errors:**

- `422` - Validation error (invalid email, phone, password)
- `409` - Email or phone already registered

---

### POST /api/auth/login

Login with email or phone and password.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "rememberMe": false
}
```

Or use `phone` instead of `email`.

**Response:** `200 OK`

```json
{
  "message": "Login successful",
  "data": {
    "user": { /* user object */ }
  }
}
```

**Errors:**

- `401` - Invalid credentials
- `400` - Missing email/phone or password

---

### POST /api/auth/logout

Logout the current user.

**Response:** `200 OK`

```json
{
  "message": "Logged out successfully"
}
```

---

### GET /api/auth/verify

Get current authenticated user information. Requires authentication.

**Response:** `200 OK`

```json
{
  "message": "User verified",
  "data": {
    "user": { /* user object */ }
  }
}
```

**Errors:**

- `401` - Not authenticated

---

### POST /api/auth/change-password

Change user password. Requires authentication.

**Request Body:**

```json
{
  "oldPassword": "currentPassword",
  "newPassword": "newPassword123"
}
```

**Response:** `200 OK`

```json
{
  "message": "Password changed successfully"
}
```

**Errors:**

- `401` - Invalid current password
- `422` - New password too short

---

## Users

### GET /api/users/{userId}

Get user profile by ID.

**Response:** `200 OK`

```json
{
  "message": "User retrieved successfully",
  "data": {
    "user": {
      "_id": "user_id",
      "email": "user@example.com",
      "phone": "+1234567890",
      "fullName": "John Doe",
      "role": "provider",
      "rating": 4.5,
      "totalReviews": 12,
      "address": "123 Main St",
      "city": "New York",
      "area": "Downtown",
      "profileImage": "/uploads/profilepic.jpg"
    }
  }
}
```

**Errors:**

- `404` - User not found
- `400` - Invalid user ID

---

### PUT /api/users/{userId}

Update user profile. Can only update own profile.

**Request Body:**

```json
{
  "fullName": "Jane Doe",
  "address": "456 Oak Ave",
  "city": "Los Angeles",
  "area": "Downtown",
  "profileImage": "/uploads/new_profile.jpg"
}
```

**Response:** `200 OK`

```json
{
  "message": "Profile updated successfully",
  "data": {
    "user": { /* updated user object */ }
  }
}
```

**Errors:**

- `401` - Not authenticated
- `403` - Cannot update other users' profiles
- `409` - Phone number already in use

---

### GET /api/users/me

Get current authenticated user profile.

**Response:** `200 OK`

```json
{
  "message": "Current user retrieved",
  "data": {
    "user": { /* current user object */ }
  }
}
```

**Errors:**

- `401` - Not authenticated

---

### PUT /api/users/me/profile

Update current user profile.

Same as `PUT /api/users/{userId}` but for current user.

---

### GET /api/users/{userId}/ratings

Get all ratings for a provider.

**Query Parameters:**

- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10, max: 100)

**Response:** `200 OK`

```json
{
  "message": "Ratings retrieved successfully",
  "data": {
    "ratings": [
      {
        "_id": "rating_id",
        "bookingId": "booking_id",
        "customerId": "customer_id",
        "rating": 5,
        "review": "Great service!",
        "createdAt": "2026-04-10T15:30:00"
      }
    ],
    "averageRating": 4.8,
    "totalRatings": 12,
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 12
    }
  }
}
```

---

## Services

### GET /api/services/categories

Get all service categories with subcategories.

**Query Parameters:**

- `search`: Search by category name
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10)

**Response:** `200 OK`

```json
{
  "message": "Categories retrieved successfully",
  "data": {
    "categories": [
      {
        "_id": "category_id",
        "name": "Home Maintenance",
        "nameUrdu": "گھر کی دیکھ بھال",
        "icon": "🏠",
        "displayOrder": 1,
        "subcategories": [
          {
            "name": "AC Repair",
            "nameUrdu": "AC کی مرمت",
            "basePrice": 50,
            "priceUnit": "per_visit",
            "estimatedDuration": 120
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5
    }
  }
}
```

---

### GET /api/services/categories/{categoryId}

Get a specific category with subcategories.

**Response:** `200 OK`

```json
{
  "message": "Category retrieved successfully",
  "data": {
    "category": { /* category object with subcategories */ }
  }
}
```

---

### GET /api/services/categories/{categoryId}/subcategories

Get subcategories for a category.

**Response:** `200 OK`

```json
{
  "message": "Subcategories retrieved successfully",
  "data": {
    "subcategories": [
      {
        "name": "AC Repair",
        "basePrice": 50,
        "priceUnit": "per_visit",
        "estimatedDuration": 120
      }
    ]
  }
}
```

---

### POST /api/services/admin/categories (Admin Only)

Create a new service category.

**Request Body:**

```json
{
  "name": "Home Maintenance",
  "nameUrdu": "گھر کی دیکھ بھال",
  "icon": "🏠",
  "displayOrder": 1,
  "subcategories": [
    {
      "name": "AC Repair",
      "basePrice": 50,
      "priceUnit": "per_visit"
    }
  ]
}
```

**Response:** `201 Created`

---

### PUT /api/services/admin/categories/{categoryId} (Admin Only)

Update a service category.

**Request Body:** Same as POST

**Response:** `200 OK`

---

### DELETE /api/services/admin/categories/{categoryId} (Admin Only)

Delete a service category.

**Response:** `200 OK`

```json
{
  "message": "Category deleted successfully"
}
```

---

## Bookings

### POST /api/bookings

Create a new booking. Customers only.

**Request Body:**

```json
{
  "subcategoryName": "AC Repair",
  "baseAmount": 100,
  "preferredDate": "2026-04-20",
  "preferredTimeSlot": "10:00-11:00",
  "location": {
    "address": "123 Main St",
    "city": "New York",
    "area": "Downtown"
  },
  "problemDescription": "AC not cooling properly",
  "specialInstructions": "Please call 10 mins before arrival",
  "additionalCharges": 0,
  "discountAmount": 0
}
```

**Response:** `201 Created`

```json
{
  "message": "Booking created successfully",
  "data": {
    "booking": {
      "_id": "booking_id",
      "customerId": "customer_id",
      "providerId": null,
      "status": "pending",
      "baseAmount": 100,
      "additionalCharges": 0,
      "discountAmount": 0,
      "totalAmount": 100,
      "paymentStatus": "pending",
      "createdAt": "2026-04-11T10:00:00"
    }
  }
}
```

**Errors:**

- `401` - Not authenticated
- `403` - Only customers can create bookings
- `422` - Validation error

---

### GET /api/bookings

List user bookings. Customers see their own.

**Query Parameters:**

- `status`: Filter by status (pending, confirmed, assigned, in_progress, completed, cancelled)
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10)

**Response:** `200 OK`

```json
{
  "message": "Bookings retrieved successfully",
  "data": {
    "bookings": [ /* array of booking objects */ ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5
    }
  }
}
```

---

### GET /api/bookings/{bookingId}

Get booking details.

**Response:** `200 OK`

```json
{
  "message": "Booking retrieved successfully",
  "data": {
    "booking": { /* booking object */ }
  }
}
```

---

### PUT /api/bookings/{bookingId}

Update booking details.

**Request Body:**

```json
{
  "status": "confirmed",
  "additionalCharges": 20,
  "discountAmount": 10,
  "problemDescription": "Updated description"
}
```

**Response:** `200 OK`

---

### PUT /api/bookings/{bookingId}/status

Update booking status (supports state machine validation).

**Request Body:**

```json
{
  "status": "confirmed" // or: assigned, in_progress, completed, cancelled
}
```

**Valid Status Transitions:**

- pending → confirmed, cancelled
- confirmed → assigned, cancelled
- assigned → in_progress, cancelled
- in_progress → completed
- completed → (no transitions)
- cancelled → (no transitions)

**Response:** `200 OK`

**Errors:**

- `422` - Invalid status transition

---

### PUT /api/bookings/{bookingId}/assign-provider (Admin Only)

Assign a provider to a booking.

**Request Body:**

```json
{
  "providerId": "provider_id"
}
```

**Response:** `200 OK`

---

## Ratings

### POST /api/ratings/bookings/{bookingId}

Rate a completed booking. Customers only.

**Request Body:**

```json
{
  "rating": 5,
  "review": "Excellent service, highly recommended!"
}
```

**Response:** `201 Created`

```json
{
  "message": "Rating created successfully",
  "data": {
    "rating": {
      "_id": "rating_id",
      "bookingId": "booking_id",
      "customerId": "customer_id",
      "providerId": "provider_id",
      "rating": 5,
      "review": "Excellent service!",
      "createdAt": "2026-04-11T14:00:00"
    }
  }
}
```

**Errors:**

- `401` - Not authenticated
- `403` - Only customers can rate
- `404` - Booking not found
- `409` - Booking already rated
- `422` - Can only rate completed bookings, invalid rating value

---

### GET /api/ratings/bookings/{bookingId}

Get rating for a booking.

**Response:** `200 OK`

```json
{
  "message": "Rating retrieved successfully",
  "data": {
    "rating": { /* rating object or null */ }
  }
}
```

---

### PUT /api/ratings/bookings/{bookingId}

Update a rating (review text only).

**Request Body:**

```json
{
  "review": "Updated review text"
}
```

**Response:** `200 OK`

---

### GET /api/ratings/providers/{providerId}

Get all ratings for a provider.

**Query Parameters:**

- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10)

**Response:** `200 OK`

```json
{
  "message": "Provider ratings retrieved successfully",
  "data": {
    "ratings": [ /* array of rating objects */ ],
    "providerStats": {
      "providerId": "provider_id",
      "averageRating": 4.8,
      "totalRatings": 12
    },
    "pagination": { /* pagination info */ }
  }
}
```

---

### GET /api/ratings/providers/{providerId}/stats

Get rating statistics for a provider.

**Response:** `200 OK`

```json
{
  "message": "Provider statistics retrieved successfully",
  "data": {
    "averageRating": 4.8,
    "totalRatings": 12
  }
}
```

---

## Payments

### POST /api/payments/create-intent

Create a Stripe payment intent for a booking.

**Request Body:**

```json
{
  "bookingId": "booking_id",
  "currency": "usd"
}
```

**Response:** `200 OK`

```json
{
  "message": "Payment intent created successfully",
  "data": {
    "clientSecret": "pi_xxx_secret_xxx",
    "paymentIntentId": "pi_xxx",
    "amount": 100,
    "currency": "usd",
    "status": "requires_payment_method"
  }
}
```

---

### POST /api/payments/confirm

Confirm a payment.

**Request Body:**

```json
{
  "bookingId": "booking_id",
  "paymentIntentId": "pi_xxx"
}
```

**Response:** `200 OK`

```json
{
  "message": "Payment confirmation processed",
  "data": {
    "success": true,
    "paymentIntentId": "pi_xxx",
    "status": "succeeded",
    "chargeId": "ch_xxx"
  }
}
```

---

### POST /api/payments/refund (Admin Only)

Refund a payment.

**Request Body:**

```json
{
  "paymentIntentId": "pi_xxx",
  "amount": 100 // Optional, full refund if omitted
}
```

**Response:** `200 OK`

```json
{
  "message": "Payment refunded successfully",
  "data": {
    "refundId": "re_xxx",
    "amount": 100,
    "status": "succeeded"
  }
}
```

---

### POST /api/payments/webhook

Stripe webhook handler (automatically updates booking payment status).

---

## Admin

### GET /api/admin/bookings

Get all system bookings. Admin only.

**Query Parameters:**

- `status`: Filter by status
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10)

**Response:** `200 OK`

---

### GET /api/admin/users

Get all users. Admin only.

**Query Parameters:**

- `role`: Filter by role (customer, provider)
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10)

**Response:** `200 OK`

---

### GET /api/admin/stats

Get system statistics. Admin only.

**Response:** `200 OK`

```json
{
  "message": "System statistics retrieved successfully",
  "data": {
    "totalUsers": 150,
    "activeUsers": 120,
    "customers": 100,
    "providers": 50,
    "totalBookings": 500,
    "pendingBookings": 25,
    "completedBookings": 450,
    "totalCategories": 10,
    "totalRevenue": 25000
  }
}
```

---

### GET /api/admin/bookings/breakdown

Get booking breakdown by status. Admin only.

**Response:** `200 OK`

```json
{
  "message": "Booking breakdown retrieved successfully",
  "data": {
    "pending": { "count": 25, "totalAmount": 2500 },
    "completed": { "count": 450, "totalAmount": 45000 }
  }
}
```

---

### GET /api/admin/providers/performance

Get top performing providers. Admin only.

**Response:** `200 OK`

```json
{
  "message": "Provider performance retrieved successfully",
  "data": {
    "providers": [
      {
        "providerId": "provider_id",
        "completedJobs": 50,
        "totalRevenue": 5000,
        "averageRating": 4.8
      }
    ]
  }
}
```

---

### POST /api/admin/users/{userId}/deactivate (Admin Only)

Deactivate a user account.

**Response:** `200 OK`

---

### POST /api/admin/users/{userId}/activate (Admin Only)

Activate a user account.

**Response:** `200 OK`

---

### POST /api/admin/categories

Create service category. Admin only.

(Same as POST /api/services/admin/categories)

---

### PUT /api/admin/categories/{categoryId}

Update service category. Admin only.

---

### DELETE /api/admin/categories/{categoryId}

Delete service category. Admin only.

---

## Uploads

### POST /api/uploads

Upload a file (image).

**Request:** multipart/form-data

- `file`: Image file (PNG, JPG, JPEG, GIF, WEBP)

**Response:** `201 Created`

```json
{
  "message": "File uploaded successfully",
  "data": {
    "url": "/uploads/uuid_timestamp.jpg",
    "filename": "uuid_timestamp.jpg",
    "originalFilename": "profile.jpg",
    "size": 102400,
    "uploadedAt": "2026-04-11T10:00:00"
  }
}
```

**Errors:**

- `400` - No file provided, invalid file type
- `413` - File too large

---

### GET /api/uploads/{filename}

Download an uploaded file.

**Response:** Binary file content

---

### DELETE /api/uploads/{filename}

Delete an uploaded file. Authenticated users only.

**Response:** `200 OK`

```json
{
  "message": "File deleted successfully"
}
```

---

## Error Handling

All errors return JSON with this format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

- `VALIDATION_ERROR` (422) - Invalid input data
- `NOT_FOUND` (404) - Resource not found
- `UNAUTHORIZED` (401) - Authentication required
- `FORBIDDEN` (403) - Permission denied
- `CONFLICT` (409) - Resource conflict (duplicate)
- `INTERNAL_ERROR` (500) - Server error
- `INVALID_ID` (400) - Invalid object ID format
- `INVALID_REQUEST` (400) - Missing required fields

---

## Development Notes

1. **Logging:** All requests/responses logged to `logs/zeetech_backend.log` and console
2. **Database:** MongoDB with automatic collection initialization
3. **Session:** Secure session cookies (30 days)
4. **CORS:** Configured for Flutter frontend
5. **File Uploads:** Max 16MB, stored in `uploads/` directory
6. **Rate Limiting:** Not implemented (add in production)
