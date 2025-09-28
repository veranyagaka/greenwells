# LPG Delivery Platform - Integration Guide

This guide explains how to integrate the frontend with a Django backend and deploy the complete system.

## Project Structure

```
LPG Delivery Platform/
├── frontend/                 # Next.js React Frontend
│   ├── app/                 # Next.js App Router
│   ├── components/          # React Components
│   ├── lib/                 # API utilities and helpers
│   ├── types/               # TypeScript definitions
│   ├── package.json         # Frontend dependencies
│   └── .env.local           # Frontend environment variables
├── backend/                 # Django Backend
│   ├── manage.py            # Django management script
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Backend environment variables
│   └── lpg_delivery/        # Django project (to be created)
├── setup.py                 # Project setup script
├── package.json             # Root package.json with scripts
└── README.md                # Project documentation
```

## Quick Start

### 1. Initial Setup

Run the setup script to initialize both frontend and backend:

```bash
python setup.py
```

This will:
- Install frontend dependencies
- Create Python virtual environment
- Install backend dependencies
- Create environment files from examples

### 2. Frontend Development

```bash
# Start frontend development server
npm run dev:frontend
# or
cd frontend && npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Backend Development

```bash
# Start Django development server
npm run dev:backend
# or
cd backend && python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

## API Integration

### Frontend Configuration

The frontend is configured to work with Django through:

1. **Environment Variables** (`frontend/.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

2. **API Client** (`frontend/lib/api.ts`):
   - JWT authentication
   - RESTful API calls
   - WebSocket connections
   - Error handling

### Backend Configuration

The Django backend should be configured with:

1. **CORS Settings** for frontend domains
2. **JWT Authentication** for secure API access
3. **WebSocket Support** for real-time features
4. **Database Models** for orders, users, vehicles, tracking

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/refresh/` - Token refresh

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Get order details
- `PATCH /api/orders/{id}/` - Update order

### Drivers & Vehicles
- `GET /api/drivers/` - List drivers
- `POST /api/drivers/{id}/location/` - Update driver location
- `GET /api/vehicles/` - List vehicles

### Tracking
- `GET /api/tracking/active/` - Get active deliveries
- `POST /api/tracking/{id}/gps/` - Submit GPS location

### WebSocket Endpoints
- `ws://localhost:8000/ws/tracking/{order_id}/` - Order tracking
- `ws://localhost:8000/ws/driver/{driver_id}/location/` - Driver location

## Development Workflow

### 1. Start Both Services

```bash
# Terminal 1: Backend
npm run dev:backend

# Terminal 2: Frontend
npm run dev:frontend
```

### 2. API Development

1. Create Django models and serializers
2. Update frontend API calls in `lib/api.ts`
3. Test API endpoints with frontend
4. Implement real-time features with WebSockets

### 3. Frontend Development

1. Create React components in `components/`
2. Use API utilities from `lib/api.ts`
3. Implement real-time updates with WebSocket helpers
4. Test with mock data or real backend

## Deployment

### Frontend Deployment

1. **Build for Production**:
   ```bash
   cd frontend
   npm run build:production
   ```

2. **Deploy to Vercel/Netlify**:
   - Connect your repository
   - Set environment variables
   - Deploy automatically

### Backend Deployment

1. **Configure Production Settings**:
   - Set `DEBUG=False`
   - Configure production database
   - Set up Redis for caching
   - Configure CORS for production domains

2. **Deploy to Heroku/DigitalOcean**:
   - Set up PostgreSQL database
   - Configure Redis instance
   - Deploy Django application
   - Set up SSL certificates

### Environment Variables

#### Frontend (Production)
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api
NEXT_PUBLIC_WS_URL=wss://your-backend-domain.com/ws
NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain.com
```

#### Backend (Production)
```env
DEBUG=False
ALLOWED_HOSTS=your-backend-domain.com
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port/0
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## Testing

### Frontend Testing
```bash
cd frontend
npm run test
```

### Backend Testing
```bash
cd backend
python manage.py test
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS settings in Django
2. **Authentication Issues**: Verify JWT configuration
3. **WebSocket Connection**: Check Django Channels setup
4. **Build Errors**: Ensure all dependencies are installed

### Debug Mode

Enable debug mode in both frontend and backend for development:

- Frontend: `NODE_ENV=development`
- Backend: `DEBUG=True`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## Support

For issues and questions:
1. Check the documentation
2. Review the API endpoints
3. Test with the provided examples
4. Create an issue in the repository
