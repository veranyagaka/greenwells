# Frontend-Backend Connection Setup

This guide will help you connect the Next.js frontend with the Django backend for the GreenWells LPG delivery platform.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script from the project root
./setup-connection.sh
```

### Option 2: Manual Setup

## 📋 Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- Git

## 🔧 Backend Setup (Django)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the Django server:**
   ```bash
   python manage.py runserver 8000
   ```

The backend will be available at `http://localhost:8000`

## 🎨 Frontend Setup (Next.js)

1. **Navigate to frontend directory:**
   ```bash
   cd main-frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.local.example .env.local
   ```

4. **Start the Next.js development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## 🔗 Connection Configuration

### Backend Configuration (Django)

The backend has been configured with:

- **CORS Headers**: Allows requests from `localhost:3000`
- **JWT Authentication**: Token-based authentication
- **API Endpoints**: RESTful API structure

Key settings in `backend/backend/settings.py`:
```python
# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Development only
```

### Frontend Configuration (Next.js)

The frontend has been configured with:

- **API Base URL**: Points to Django backend
- **Authentication**: JWT token management
- **Environment Variables**: Proper configuration

Key settings in `main-frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_MOCK_API=false
```

## 🛠️ API Endpoints

### Authentication Endpoints
- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/signout/` - User logout
- `POST /api/auth/refresh/` - Token refresh

### Order Management Endpoints
- `GET /api/orders/` - List orders
- `POST /api/orders/create/` - Create order
- `GET /api/orders/{id}/` - Get specific order
- `PATCH /api/orders/{id}/status/` - Update order status

### Vehicle Management Endpoints
- `GET /api/vehicles/` - List vehicles
- `POST /api/vehicles/create/` - Create vehicle
- `GET /api/vehicles/{id}/` - Get specific vehicle

### Cylinder Management Endpoints
- `GET /api/cylinders/` - List cylinders
- `POST /api/cylinders/register/` - Register cylinder
- `POST /api/cylinders/scan/` - Scan cylinder
- `GET /api/cylinders/{id}/` - Get cylinder details

## 🧪 Testing the Connection

1. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && python manage.py runserver 8000
   
   # Terminal 2 - Frontend
   cd main-frontend && npm run dev
   ```

2. **Test authentication:**
   - Open `http://localhost:3000`
   - Try registering a new user
   - Test login functionality
   - Check browser console for errors

3. **Test API endpoints:**
   ```bash
   # Test backend health
   curl http://localhost:8000/api/auth/login/
   
   # Test with authentication
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/orders/
   ```

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Ensure `django-cors-headers` is installed
   - Check CORS settings in Django settings
   - Verify frontend URL in `CORS_ALLOWED_ORIGINS`

2. **Authentication Errors:**
   - Check JWT token format
   - Verify token expiration
   - Ensure proper Authorization header

3. **API Connection Errors:**
   - Verify backend is running on port 8000
   - Check `.env.local` file configuration
   - Ensure API URLs are correct

4. **Database Errors:**
   - Run migrations: `python manage.py migrate`
   - Check database configuration
   - Verify database file permissions

### Debug Mode

Enable debug logging in Django:
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📚 Development Workflow

1. **Make changes to backend:**
   - Update models, views, or serializers
   - Run migrations if needed
   - Test API endpoints

2. **Make changes to frontend:**
   - Update components or pages
   - Test API integration
   - Check for TypeScript errors

3. **Test integration:**
   - Test authentication flow
   - Test data flow between frontend and backend
   - Check error handling

## 🚀 Production Deployment

For production deployment:

1. **Backend:**
   - Set `DEBUG = False`
   - Configure proper database
   - Set up proper CORS origins
   - Use environment variables for secrets

2. **Frontend:**
   - Build production bundle: `npm run build`
   - Update API URLs for production
   - Configure proper environment variables

## 📞 Support

If you encounter issues:

1. Check the browser console for errors
2. Check Django server logs
3. Verify all dependencies are installed
4. Ensure both servers are running
5. Check network connectivity

## 🎯 Next Steps

After successful connection:

1. Test all authentication flows
2. Implement order management features
3. Add real-time tracking capabilities
4. Test cylinder management features
5. Add error handling and validation
