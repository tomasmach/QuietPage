# Auth API Endpoints Documentation

This document describes the authentication API endpoints for the QuietPage React frontend.

## Base URL
All endpoints are prefixed with `/api/v1/`

## Endpoints Overview

### 1. CSRF Token (GET `/api/v1/auth/csrf/`)
Get a CSRF token for subsequent requests.

**Request:**
```http
GET /api/v1/auth/csrf/
```

**Response (200 OK):**
```json
{
  "csrfToken": "abc123..."
}
```

**Notes:**
- No authentication required
- Sets CSRF cookie automatically
- Call this before making any POST requests from React

**React Example:**
```javascript
const response = await fetch('/api/v1/auth/csrf/', {
  credentials: 'include',  // Important for session cookies
});
const { csrfToken } = await response.json();
```

---

### 2. Register (POST `/api/v1/auth/register/`)
Create a new user account and automatically log in.

**Request:**
```http
POST /api/v1/auth/register/
Content-Type: application/json
X-CSRFToken: <token>

{
  "username": "jan.novak",
  "email": "jan@example.com",
  "password": "SecurePassword123",
  "password_confirm": "SecurePassword123"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "jan.novak",
    "email": "jan@example.com",
    "first_name": "",
    "last_name": "",
    "avatar": null,
    "bio": "",
    "timezone": "Europe/Prague",
    "daily_word_goal": 750,
    "current_streak": 0,
    "longest_streak": 0,
    "email_notifications": false,
    "preferred_writing_time": "morning",
    "reminder_enabled": false,
    "reminder_time": "08:00:00"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "errors": {
    "username": ["Uživatel s tímto uživatelským jménem již existuje."],
    "email": ["Uživatel s touto emailovou adresou již existuje."],
    "password": ["Heslo je příliš podobné uživatelskému jménu."],
    "password_confirm": ["Hesla se neshodují."]
  }
}
```

**Validation:**
- Username must be unique (case-insensitive)
- Email must be unique (case-insensitive)
- Password must match password_confirm
- Password strength validated by Django validators:
  - Minimum 8 characters
  - Not too similar to username/email
  - Not a common password
  - Not entirely numeric

**React Example:**
```javascript
const response = await fetch('/api/v1/auth/register/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken,
  },
  body: JSON.stringify({
    username: 'jan.novak',
    email: 'jan@example.com',
    password: 'SecurePassword123',
    password_confirm: 'SecurePassword123',
  }),
});
const data = await response.json();
```

---

### 3. Login (POST `/api/v1/auth/login/`)
Authenticate with username or email.

**Request:**
```http
POST /api/v1/auth/login/
Content-Type: application/json
X-CSRFToken: <token>

{
  "username_or_email": "jan.novak",
  "password": "SecurePassword123"
}
```

OR with email:

```json
{
  "username_or_email": "jan@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "jan.novak",
    "email": "jan@example.com",
    "first_name": "",
    "last_name": "",
    "avatar": null,
    "bio": "",
    "timezone": "Europe/Prague",
    "daily_word_goal": 750,
    "current_streak": 0,
    "longest_streak": 0,
    "email_notifications": false,
    "preferred_writing_time": "morning",
    "reminder_enabled": false,
    "reminder_time": "08:00:00"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Neplatné přihlašovací údaje."
}
```

OR if account is inactive:

```json
{
  "error": "Tento účet byl deaktivován."
}
```

**Notes:**
- Accepts username or email (detected by presence of @)
- Sets session cookie on success
- Protected by django-axes (5 failed attempts = 15 min lockout)

**React Example:**
```javascript
const response = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken,
  },
  body: JSON.stringify({
    username_or_email: 'jan.novak',
    password: 'SecurePassword123',
  }),
});
const data = await response.json();
```

---

### 4. Current User (GET `/api/v1/auth/me/`)
Get currently authenticated user data.

**Request:**
```http
GET /api/v1/auth/me/
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "jan.novak",
    "email": "jan@example.com",
    "first_name": "Jan",
    "last_name": "Novák",
    "avatar": "http://localhost:8000/media/avatars/2025/01/profile.jpg",
    "bio": "Milovník psaní a sebereflexe.",
    "timezone": "Europe/Prague",
    "daily_word_goal": 750,
    "current_streak": 5,
    "longest_streak": 12,
    "email_notifications": true,
    "preferred_writing_time": "morning",
    "reminder_enabled": true,
    "reminder_time": "08:00:00"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Notes:**
- Requires authentication (session cookie)
- Returns full user profile data

**React Example:**
```javascript
const response = await fetch('/api/v1/auth/me/', {
  credentials: 'include',
});
if (response.ok) {
  const { user } = await response.json();
  // User is authenticated
} else {
  // User is not authenticated
}
```

---

### 5. Logout (POST `/api/v1/auth/logout/`)
Destroy user session.

**Request:**
```http
POST /api/v1/auth/logout/
```

**Response (200 OK):**
```json
{
  "message": "Úspěšně odhlášeno."
}
```

**Notes:**
- No authentication required
- Safe to call even if not logged in
- Destroys session cookie

**React Example:**
```javascript
const response = await fetch('/api/v1/auth/logout/', {
  method: 'POST',
  credentials: 'include',
});
const data = await response.json();
```

---

## Security Features

### CSRF Protection
All POST endpoints (except logout and csrf) require CSRF token:
1. Call `GET /api/v1/auth/csrf/` to get token
2. Include token in `X-CSRFToken` header for POST requests

### Session-Based Authentication
- Uses Django sessions (not JWT tokens)
- Session cookie lasts 14 days with activity refresh
- CORS configured for `localhost:5173` in development

### Rate Limiting
- django-axes provides brute force protection
- 5 failed login attempts = 15 minute lockout
- Lockout is per username+IP combination
- Counter resets on successful login

### Password Validation
- Minimum 8 characters
- Cannot be too similar to username/email
- Cannot be a common password
- Cannot be entirely numeric

### Data Privacy
- Passwords never returned in responses
- Only authenticated user can access their own data
- All endpoints return Czech error messages

---

## React Integration Example

```javascript
// 1. Initialize CSRF token on app load
async function initAuth() {
  const response = await fetch('/api/v1/auth/csrf/', {
    credentials: 'include',
  });
  const { csrfToken } = await response.json();
  return csrfToken;
}

// 2. Check if user is authenticated
async function getCurrentUser() {
  const response = await fetch('/api/v1/auth/me/', {
    credentials: 'include',
  });
  if (response.ok) {
    const { user } = await response.json();
    return user;
  }
  return null;
}

// 3. Login function
async function login(csrfToken, username_or_email, password) {
  const response = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ username_or_email, password }),
  });

  if (response.ok) {
    const { user } = await response.json();
    return { success: true, user };
  } else {
    const { error } = await response.json();
    return { success: false, error };
  }
}

// 4. Register function
async function register(csrfToken, username, email, password, password_confirm) {
  const response = await fetch('/api/v1/auth/register/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ username, email, password, password_confirm }),
  });

  if (response.ok) {
    const { user } = await response.json();
    return { success: true, user };
  } else {
    const { errors } = await response.json();
    return { success: false, errors };
  }
}

// 5. Logout function
async function logout() {
  const response = await fetch('/api/v1/auth/logout/', {
    method: 'POST',
    credentials: 'include',
  });
  return response.ok;
}
```

---

## Testing

Test the endpoints using curl:

```bash
# 1. Get CSRF token
curl -c cookies.txt http://localhost:8000/api/v1/auth/csrf/

# 2. Register new user
curl -b cookies.txt -c cookies.txt -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token-from-step-1>" \
  -d '{"username":"test","email":"test@example.com","password":"TestPass123","password_confirm":"TestPass123"}' \
  http://localhost:8000/api/v1/auth/register/

# 3. Get current user
curl -b cookies.txt http://localhost:8000/api/v1/auth/me/

# 4. Logout
curl -b cookies.txt -X POST http://localhost:8000/api/v1/auth/logout/

# 5. Login
curl -b cookies.txt -c cookies.txt -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{"username_or_email":"test","password":"TestPass123"}' \
  http://localhost:8000/api/v1/auth/login/
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, POST /logout) |
| 201 | Created (POST /register) |
| 400 | Bad Request (validation errors, invalid credentials) |
| 401 | Unauthorized (authentication required) |
| 403 | Forbidden (rate limited by django-axes) |

---

## Notes for Frontend Developers

1. **Always include `credentials: 'include'`** in fetch options to send session cookies
2. **Store CSRF token** in React state/context after getting it
3. **Handle 401 responses** by redirecting to login page
4. **Handle 403 responses** from django-axes with appropriate lockout message
5. **Session cookies are httpOnly** - you cannot access them from JavaScript
6. **CORS is configured** for `localhost:5173` in development settings
7. **All responses are in Czech** - you may want to add translation layer
