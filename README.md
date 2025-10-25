# GreenWells LPG Fleet Management System

> **IMPORTANT**: This is a MONOREPO. Next.js is in `main-frontend/`, Django is in `backend/`

## 🚀 Quick Start

```bash
# Install all dependencies
npm run install:all

# Start both servers
npm run dev

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## 📁 Project Structure

```
greenwells/
├── main-frontend/      # ← NEXT.JS IS HERE
│   └── package.json   # Next.js dependencies
├── backend/            # ← DJANGO IS HERE
│   └── requirements.txt
└── package.json        # Root orchestration only
```

## ⚠️ About "No Next.js Version Detected" Warning

**This is a FALSE POSITIVE. Your setup is correct!**

The warning appears because Next.js is in `main-frontend/` (as it should be for a monorepo), not in the root.

**Ignore this warning** - everything works perfectly.

## 🎯 Greenwells LPG Fleet Management System

A comprehensive fleet management and delivery tracking system for LPG (Liquefied Petroleum Gas) distribution, featuring QR/RFID cylinder tracking, real-time delivery monitoring, and enterprise-level security.

## 🚀 Features

### Core Functionality
- **Order Management**: Complete order lifecycle from creation to delivery
- **Fleet Management**: Vehicle and driver assignment with real-time tracking
- **Delivery Tracking**: GPS-based real-time delivery monitoring
- **Customer Portal**: Self-service order placement and tracking

### Cylinder Tracking (QR/RFID)
- **Authenticity Verification**: QR/RFID code scanning with cryptographic validation
- **Complete History**: Track every cylinder from registration to retirement
- **Tamper Detection**: Automated suspicious activity detection
- **Security Audit**: Complete compliance-ready audit trail

### Security
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Customer, Driver, Dispatcher, and Admin roles
- **Cryptographic Security**: SHA-256 hashing for cylinder verification
- **Audit Logging**: Complete trail of all system actions

## 📋 Prerequisites

### Backend Requirements
- Python 3.8 or higher
- pip (Python package manager)
- SQLite (development) / PostgreSQL (production)

### Frontend Requirements
- Node.js 16.x or higher
- npm or yarn

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/veranyagaka/greenwells.git
cd greenwells
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

**Admin Interface**: `http://localhost:8000/admin`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd main-frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test orders
python manage.py test users

# Run with verbose output
python manage.py test --verbosity=2
```

Expected output:
```
Ran 25 tests in 23.052s
OK
```

### Frontend Tests

```bash
cd main-frontend
npm test
```

## 📖 API Documentation

### Authentication

All API endpoints require JWT authentication. Include the token in the Authorization header:

```bash
Authorization: ******
```

### Quick API Examples

#### 1. User Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

#### 2. Create Order (Customer)
```bash
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_address": "123 Main St, Nairobi",
    "quantity_kg": 13.0,
    "scheduled_time": "2024-01-20T10:00:00Z",
    "customer_phone": "+254712345678"
  }'
```

#### 3. Scan Cylinder (QR/RFID)
```bash
curl -X POST http://localhost:8000/api/cylinders/scan/ \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "QR-A1B2C3D4E5F67890",
    "scan_type": "QR",
    "location_lat": -1.2921,
    "location_lng": 36.8219
  }'
```

### Complete API Documentation

For detailed API documentation, see:
- **Backend API**: `backend/CYLINDER_API_DOCUMENTATION.md`
- **Quick Start Guide**: `backend/CYLINDER_QUICK_START.md`
- **Security Guide**: `backend/CYLINDER_SECURITY_GUIDE.md`
- **User Authentication**: `backend/users/README.md`

## 🏗️ Project Structure

```
greenwells/
├── backend/                          # Django REST Framework backend
│   ├── backend/                      # Project settings
│   │   ├── settings.py              # Configuration
│   │   ├── urls.py                  # URL routing
│   │   └── wsgi.py                  # WSGI config
│   ├── orders/                       # Order and fleet management
│   │   ├── models.py                # Database models
│   │   ├── serializers.py           # API serializers
│   │   ├── views.py                 # API views
│   │   ├── urls.py                  # URL routing
│   │   └── tests.py                 # Test cases
│   ├── users/                        # User authentication
│   │   ├── models.py                # User model
│   │   ├── views.py                 # Auth views
│   │   └── jwt_service.py           # JWT utilities
│   ├── manage.py                     # Django CLI
│   ├── requirements.txt              # Python dependencies
│   └── CYLINDER_*.md                 # Documentation
│
├── main-frontend/                    # Next.js frontend
│   ├── components/                   # React components
│   │   ├── CustomerDashboard.tsx    # Customer interface
│   │   ├── DriverDashboard.tsx      # Driver interface
│   │   └── ui/                      # UI components
│   ├── lib/                          # Utilities
│   │   └── api.ts                   # API integration
│   ├── types/                        # TypeScript types
│   │   └── index.ts                 # Type definitions
│   ├── app/                          # Next.js pages
│   ├── package.json                  # Node dependencies
│   └── next.config.js               # Next.js config
│
└── README.md                         # This file
```

## 👥 User Roles

### Customer
- Place and track orders
- Scan cylinders for verification
- View order history
- Manage profile and emergency contacts

### Driver
- View assigned deliveries
- Update delivery status
- Report GPS location
- Scan cylinders during delivery

### Dispatcher
- Assign orders to drivers
- Register new cylinders
- Monitor fleet status
- Manage vehicle assignments

### Admin
- Full system access
- User management
- System configuration
- Security monitoring

## 🔐 Security Features

### Cylinder Authentication
- **UUID-based Codes**: 2^122 unique combinations
- **SHA-256 Hashing**: Cryptographic verification
- **Tamper Detection**: Automated suspicious activity alerts
- **Audit Trail**: Complete compliance logging

### System Security
- **JWT Tokens**: Secure authentication with refresh tokens
- **Role-Based Access**: Granular permission control
- **HTTPS Ready**: TLS/SSL configuration support
- **Rate Limiting**: Protection against abuse

## 📊 Database Schema

### Key Models

#### Cylinder
- Unique QR/RFID codes
- Cryptographic authentication hash
- Status tracking (ACTIVE, FILLED, IN_DELIVERY, EMPTY, etc.)
- Customer and order linking

#### Order
- Customer information
- Delivery address and schedule
- Status tracking
- Driver and vehicle assignment

#### Delivery
- Real-time status updates
- GPS tracking logs
- Driver assignments
- Completion tracking

## 🌍 Environment Variables

Create a `.env` file in the backend directory:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production)
DATABASE_URL=******localhost:5432/greenwells

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=604800

# Security (Production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

## 🚀 Deployment

### Production Checklist

Backend:
- [ ] Set `DEBUG=False` in settings
- [ ] Configure PostgreSQL database
- [ ] Set up HTTPS/TLS certificates
- [ ] Configure environment variables
- [ ] Run `python manage.py collectstatic`
- [ ] Apply migrations: `python manage.py migrate`
- [ ] Set up Gunicorn/uWSGI
- [ ] Configure Nginx reverse proxy

Frontend:
- [ ] Build production bundle: `npm run build`
- [ ] Configure API_BASE_URL
- [ ] Set up CDN for static assets
- [ ] Configure environment variables

### Docker Deployment (Optional)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Apply migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version: `python --version` (should be 3.8+)
- Verify dependencies: `pip install -r requirements.txt`
- Check database connection
- Ensure migrations are applied: `python manage.py migrate`

**Frontend won't start:**
- Check Node version: `node --version` (should be 16.x+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for port conflicts (default: 3000)

**Authentication errors:**
- Verify JWT tokens are not expired
- Check Authorization header format: `******`
- Ensure user has correct role permissions

**Cylinder scan fails:**
- Verify QR/RFID code format
- Check user authentication
- Ensure cylinder exists in database
- Review scan logs for errors

## 📞 Support & Contributing

### Getting Help
- Review documentation in `backend/` folder
- Check existing issues on GitHub
- Create a new issue for bugs or feature requests

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `python manage.py test`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Create a Pull Request

### Code Style
- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Use ESLint and Prettier configurations
- Write tests for new features
- Document API changes

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- Django REST Framework
- Next.js & React
- TypeScript
- PostgreSQL/SQLite

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Status**: Production Ready ✅

For detailed implementation information, see `backend/CYLINDER_TRACKING_IMPLEMENTATION.md`
