# LPG Customer Delivery System - Authentication API

This documentation covers the authentication system for the LPG customer delivery backend, providing secure user registration, login, logout, and user information retrieval.

## Overview

The authentication system is built using Django REST Framework with a custom User model that supports different user roles in the LPG delivery system. It provides session-based authentication with robust security measures.

## User Model Schema

The system uses a custom User model with the following fields:

| Field | Type | Description | Required | Unique |
|-------|------|-------------|----------|--------|
| id | Integer | Primary key (auto-increment) | Yes | Yes |
| username | String | User's display name | Yes | Yes |
| email | String | User's email address | Yes | Yes |
| password_hash | String | Encrypted password | Yes | No |
| role | Enum | User role (CUSTOMER, DRIVER, DISPATCHER, ADMIN) | No | No |
| phone_number | String | User's phone number | No | No |
| address | Text | User's address | No | No |
| created_at | DateTime | Account creation timestamp | Auto | No |
| updated_at | DateTime | Last update timestamp | Auto | No |

## API Endpoints

### Base URL
```
http://localhost:8000/api/auth/
```

### 1. User Registration (Signup)

**Endpoint:** `POST /api/auth/signup/`

**Description:** Creates a new user account with all required details.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "role": "CUSTOMER",
  "phone_number": "+1234567890",
  "address": "123 Main Street, City, State"
}
```

**Required Fields:**
- `username`: Unique username (3-150 characters)
- `email`: Valid email address (must be unique)
- `password`: Strong password (minimum 8 characters)
- `password_confirm`: Must match password

**Optional Fields:**
- `role`: One of ['CUSTOMER', 'DRIVER', 'DISPATCHER', 'ADMIN'] (defaults to 'CUSTOMER')
- `phone_number`: User's phone number
- `address`: User's physical address

**Success Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "CUSTOMER",
    "phone_number": "+1234567890",
    "address": "123 Main Street, City, State",
    "created_at": "2023-12-01T10:30:00Z",
    "updated_at": "2023-12-01T10:30:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Registration failed",
  "details": {
    "email": ["A user with this email already exists."],
    "password_confirm": ["Passwords do not match."]
  }
}
```

### 2. User Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticates a user and creates a session.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "CUSTOMER",
    "phone_number": "+1234567890",
    "address": "123 Main Street, City, State",
    "created_at": "2023-12-01T10:30:00Z",
    "updated_at": "2023-12-01T10:30:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Login failed",
  "details": {
    "non_field_errors": ["Invalid email or password."]
  }
}
```

### 3. User Logout (Signout)

**Endpoint:** `POST /api/auth/signout/`

**Description:** Logs out the authenticated user and destroys the session.

**Authentication Required:** Yes

**Request Body:** Empty

**Success Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 4. Get User Information

**Endpoint:** `GET /api/auth/userinfo/`

**Description:** Retrieves the authenticated user's information.

**Authentication Required:** Yes

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "CUSTOMER",
    "phone_number": "+1234567890",
    "address": "123 Main Street, City, State",
    "created_at": "2023-12-01T10:30:00Z",
    "updated_at": "2023-12-01T10:30:00Z"
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Security Features

### Password Security
- **Minimum Length:** 8 characters
- **Django Validation:** Uses Django's built-in password validators
- **Hashing:** Passwords are securely hashed using Django's default hasher (PBKDF2)
- **No Storage:** Plain text passwords are never stored

### Authentication
- **Session-based:** Uses Django's session framework for authentication
- **CSRF Protection:** Custom CSRF handling for API endpoints
- **Input Validation:** Comprehensive input validation and sanitization
- **Error Handling:** Secure error messages that don't leak sensitive information

### Data Validation
- **Email Validation:** Ensures valid email format and uniqueness
- **Username Validation:** Ensures uniqueness and appropriate length
- **Role Validation:** Restricts roles to predefined values
- **Input Sanitization:** All inputs are validated and sanitized

## Usage Examples

### Using curl

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_doe",
    "email": "jane@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "role": "DRIVER",
    "phone_number": "+1987654321"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "jane@example.com",
    "password": "securepass123"
  }'
```

**Get user info (requires login):**
```bash
curl -X GET http://localhost:8000/api/auth/userinfo/ \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

**Logout:**
```bash
curl -X POST http://localhost:8000/api/auth/signout/ \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

### Using JavaScript (Frontend)

```javascript
// Register a new user
const signupData = {
  username: 'customer1',
  email: 'customer1@example.com',
  password: 'securepassword123',
  password_confirm: 'securepassword123',
  role: 'CUSTOMER',
  phone_number: '+1234567890',
  address: '123 Customer Street'
};

fetch('/api/auth/signup/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(signupData)
})
.then(response => response.json())
.then(data => console.log('Success:', data));

// Login
const loginData = {
  email: 'customer1@example.com',
  password: 'securepassword123'
};

fetch('/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include', // Important for session cookies
  body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => console.log('Login:', data));

// Get user info
fetch('/api/auth/userinfo/', {
  method: 'GET',
  credentials: 'include' // Important for session cookies
})
.then(response => response.json())
.then(data => console.log('User Info:', data));

// Logout
fetch('/api/auth/signout/', {
  method: 'POST',
  credentials: 'include' // Important for session cookies
})
.then(response => response.json())
.then(data => console.log('Logout:', data));
```

## Error Codes and Messages

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 200 | OK | Successful operation |
| 201 | Created | Successful user registration |
| 400 | Bad Request | Invalid input data, validation errors |
| 403 | Forbidden | Not authenticated for protected endpoints |
| 500 | Internal Server Error | Server-side error |

## User Roles

The system supports four user roles:

1. **CUSTOMER** - End users who order LPG deliveries
2. **DRIVER** - Delivery personnel who fulfill orders
3. **DISPATCHER** - Staff who manage and assign deliveries
4. **ADMIN** - System administrators with full access

## Best Practices

### For Frontend Developers
1. Always include `credentials: 'include'` in fetch requests for session handling
2. Handle both success and error responses appropriately
3. Validate user input on the frontend before sending to API
4. Store user information in application state after successful login
5. Implement proper logout functionality that clears local user data

### For Security
1. Use HTTPS in production environments
2. Implement rate limiting for authentication endpoints
3. Monitor failed login attempts
4. Regularly update passwords
5. Use environment variables for sensitive configuration

## Testing

The authentication system includes comprehensive tests covering:
- User model functionality
- All API endpoints (success and failure cases)
- Authentication and authorization
- Input validation and error handling

Run tests with:
```bash
python manage.py test users
```

## Logging

The system logs important authentication events:
- User registrations
- Successful logins
- Logout events
- Authentication errors

Logs can be found in Django's logging system and should be monitored in production.

## Future Enhancements

Potential improvements for the authentication system:
1. **JWT Token Support** - For stateless authentication
2. **Password Reset** - Email-based password recovery
3. **Two-Factor Authentication** - Enhanced security
4. **OAuth Integration** - Social media login support
5. **Rate Limiting** - Prevent brute force attacks
6. **Email Verification** - Verify email addresses during registration