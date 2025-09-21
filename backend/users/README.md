# LPG Customer Delivery System - JWT Authentication API

This documentation covers the JWT-based authentication system for the LPG customer delivery backend, providing secure user registration, login, logout, and user information retrieval using JSON Web Tokens.

## Overview

The authentication system is built using Django REST Framework with a custom User model that supports different user roles in the LPG delivery system. It provides **JWT-based authentication** with comprehensive security measures, token refresh capabilities, and role-based access control.

## Key Features

- **JWT Token Authentication**: Stateless authentication using JSON Web Tokens
- **Token Refresh**: Secure token refresh mechanism for extended sessions
- **Role-Based Access**: Support for different user roles (CUSTOMER, DRIVER, DISPATCHER, ADMIN)
- **Security**: Enterprise-level security with token expiration and validation
- **Scalability**: Stateless tokens perfect for microservices and mobile apps

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

**Description:** Creates a new user account and returns JWT tokens for immediate authentication.

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
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

### 2. User Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticates a user and returns JWT tokens.

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
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

### 3. Token Refresh

**Endpoint:** `POST /api/auth/refresh/`

**Description:** Generates new access and refresh tokens using a valid refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "message": "Token refreshed successfully",
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

### 4. Token Verification

**Endpoint:** `POST /api/auth/verify/`

**Description:** Verifies if the current access token is valid and returns user information.

**Authentication Required:** Yes (Bearer token in Authorization header)

**Success Response (200 OK):**
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "CUSTOMER",
    "phone_number": "+1234567890",
    "address": "123 Main Street, City, State",
    "created_at": "2023-12-01T10:30:00Z",
    "updated_at": "2023-12-01T10:30:00Z"
  },
  "message": "Token is valid"
}
```

### 5. Get User Information

**Endpoint:** `GET /api/auth/userinfo/`

**Description:** Retrieves the authenticated user's information.

**Authentication Required:** Yes (Bearer token in Authorization header)

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

### 6. User Logout (Signout)

**Endpoint:** `POST /api/auth/signout/`

**Description:** Logs out the user and invalidates the current token.

**Authentication Required:** Yes (Bearer token in Authorization header)

**Success Response (200 OK):**
```json
{
  "message": "Logout successful",
  "detail": "Token has been invalidated. Please remove it from client storage."
}
```

## JWT Token Details

### Access Token
- **Lifetime**: 24 hours (86400 seconds)
- **Purpose**: Used for API authentication
- **Contains**: User ID, email, username, role, expiration time
- **Usage**: Include in Authorization header as `Bearer <token>`

### Refresh Token
- **Lifetime**: 7 days (604800 seconds)
- **Purpose**: Used to generate new access tokens
- **Contains**: User ID, email, expiration time
- **Usage**: Send to `/api/auth/refresh/` endpoint when access token expires

### Token Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InRlc3RAZW1haWwuY29tIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciIsInJvbGUiOiJDVVNUT01FUiIsInRva2VuX3R5cGUiOiJhY2Nlc3MiLCJleHAiOjE3MDEzNDk4MDAsImlhdCI6MTcwMTI2MzQwMCwianRpIjoiYWNjZXNzXzFfMTcwMTI2MzQwMCJ9.signature
```

## Security Features

### JWT Security
- **HS256 Algorithm**: Secure HMAC SHA-256 signature
- **Token Expiration**: Automatic token expiration for security
- **Unique JTI**: JWT ID for token tracking and blacklisting
- **Type Validation**: Separate access and refresh token types
- **User Validation**: Active user check on every request

### Password Security
- **Minimum Length**: 8 characters
- **Django Validation**: Uses Django's built-in password validators
- **Hashing**: Passwords are securely hashed using Django's default hasher (PBKDF2)
- **No Storage**: Plain text passwords are never stored

### Authentication Flow
1. **Login/Signup**: User receives access and refresh tokens
2. **API Requests**: Include access token in Authorization header
3. **Token Expiry**: When access token expires, use refresh token
4. **Token Refresh**: Get new token pair using refresh token
5. **Logout**: Token is invalidated (blacklisted)

## Usage Examples

### Frontend Integration (JavaScript)

```javascript
class AuthService {
  constructor() {
    this.baseURL = '/api/auth';
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  // Register new user
  async signup(userData) {
    const response = await fetch(`${this.baseURL}/signup/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });

    if (response.ok) {
      const data = await response.json();
      this.setTokens(data.tokens);
      return data;
    }
    throw new Error('Signup failed');
  }

  // Login user
  async login(email, password) {
    const response = await fetch(`${this.baseURL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      this.setTokens(data.tokens);
      return data;
    }
    throw new Error('Login failed');
  }

  // Make authenticated request
  async makeAuthenticatedRequest(url, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.accessToken}`,
      ...options.headers
    };

    let response = await fetch(url, { ...options, headers });

    // If token expired, try refreshing
    if (response.status === 401) {
      await this.refreshAccessToken();
      headers['Authorization'] = `Bearer ${this.accessToken}`;
      response = await fetch(url, { ...options, headers });
    }

    return response;
  }

  // Refresh access token
  async refreshAccessToken() {
    const response = await fetch(`${this.baseURL}/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: this.refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      this.setTokens(data.tokens);
      return data.tokens;
    } else {
      this.logout();
      throw new Error('Token refresh failed');
    }
  }

  // Get user info
  async getUserInfo() {
    const response = await this.makeAuthenticatedRequest(`${this.baseURL}/userinfo/`);
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to get user info');
  }

  // Logout
  async logout() {
    try {
      await this.makeAuthenticatedRequest(`${this.baseURL}/signout/`, {
        method: 'POST'
      });
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      this.clearTokens();
    }
  }

  // Token management
  setTokens(tokens) {
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
    localStorage.setItem('access_token', this.accessToken);
    localStorage.setItem('refresh_token', this.refreshToken);
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isAuthenticated() {
    return !!this.accessToken;
  }
}

// Usage example
const auth = new AuthService();

// Register
await auth.signup({
  username: 'newuser',
  email: 'user@example.com',
  password: 'securepass123',
  password_confirm: 'securepass123',
  role: 'CUSTOMER'
});

// Login
await auth.login('user@example.com', 'securepass123');

// Make authenticated requests
const userInfo = await auth.getUserInfo();
console.log('User info:', userInfo);

// Logout
await auth.logout();
```

### curl Examples

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
  -d '{
    "email": "jane@example.com",
    "password": "securepass123"
  }'
```

**Get user info (with token):**
```bash
curl -X GET http://localhost:8000/api/auth/userinfo/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Refresh token:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN_HERE"
  }'
```

**Logout:**
```bash
curl -X POST http://localhost:8000/api/auth/signout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Error Codes and Messages

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 200 | OK | Successful operation |
| 201 | Created | Successful user registration |
| 400 | Bad Request | Invalid input data, validation errors |
| 401 | Unauthorized | Invalid/expired token, authentication required |
| 403 | Forbidden | Not authenticated for protected endpoints |
| 500 | Internal Server Error | Server-side error |

### JWT-Specific Error Messages

| Error | Description | Solution |
|-------|-------------|----------|
| "Token has expired" | Access token has exceeded its lifetime | Use refresh token to get new access token |
| "Invalid token" | Token is malformed or signature invalid | Login again to get new tokens |
| "Authentication credentials were not provided" | No Authorization header | Include Bearer token in Authorization header |
| "Refresh token has expired" | Refresh token has exceeded its lifetime | Login again to get new token pair |

## User Roles

The system supports four user roles:

1. **CUSTOMER** - End users who order LPG deliveries
2. **DRIVER** - Delivery personnel who fulfill orders
3. **DISPATCHER** - Staff who manage and assign deliveries
4. **ADMIN** - System administrators with full access

## Best Practices

### Frontend Development
1. **Token Storage**: Store tokens securely (avoid localStorage for sensitive apps)
2. **Automatic Refresh**: Implement automatic token refresh on 401 responses
3. **Logout Cleanup**: Always clear tokens from storage on logout
4. **Error Handling**: Handle token expiration gracefully
5. **Network Errors**: Implement retry logic for network failures

### Security Best Practices
1. **HTTPS Only**: Always use HTTPS in production
2. **Token Expiry**: Keep access token lifetime short (24 hours recommended)
3. **Refresh Rotation**: Consider rotating refresh tokens on each use
4. **Secure Storage**: Use secure storage mechanisms for tokens
5. **Logout Handling**: Implement proper logout with token cleanup

### Mobile App Integration
1. **Secure Storage**: Use keychain/keystore for token storage
2. **Background Refresh**: Refresh tokens before they expire
3. **Network Handling**: Handle offline scenarios gracefully
4. **Deep Linking**: Handle authentication state in deep links

## Testing

The JWT authentication system includes comprehensive tests covering:
- JWT token generation and verification
- All API endpoints (success and failure cases)
- Token refresh functionality
- Authentication and authorization flows
- Input validation and error handling
- Multiple user roles and permissions

Run tests with:
```bash
python manage.py test users
```

## Production Considerations

### Environment Variables
```bash
# Set in production environment
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ACCESS_TOKEN_LIFETIME=86400  # 24 hours
JWT_REFRESH_TOKEN_LIFETIME=604800  # 7 days
```

### Redis Integration (Optional)
For token blacklisting in production, consider integrating with Redis:
```python
# Example Redis blacklist implementation
import redis

class TokenBlacklist:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def blacklist_token(self, token, exp_time):
        self.redis_client.setex(f"blacklist:{token}", exp_time, "1")
    
    def is_blacklisted(self, token):
        return self.redis_client.exists(f"blacklist:{token}")
```

### Monitoring and Logging
- Monitor failed authentication attempts
- Log token generation and refresh events
- Track token usage patterns
- Set up alerts for suspicious activity

## Migration from Session-Based Auth

If migrating from session-based authentication:

1. **Gradual Migration**: Support both authentication methods temporarily
2. **Client Updates**: Update all client applications to use JWT
3. **Session Cleanup**: Remove session-based endpoints after migration
4. **Database Cleanup**: Clean up session tables if no longer needed

## Future Enhancements

Potential improvements for the JWT authentication system:
1. **Token Blacklisting**: Redis-based token blacklisting for immediate logout
2. **Multi-Device Support**: Device-specific refresh tokens
3. **OAuth Integration**: Social media login support
4. **Rate Limiting**: Advanced rate limiting per user/endpoint
5. **Audit Logging**: Comprehensive authentication event logging
6. **Token Scope**: Fine-grained permissions within tokens