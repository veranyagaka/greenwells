# GreenWells LPG Delivery Platform

## 📦 Complete Deployment Setup

A full-stack LPG delivery fleet management system with Django backend and Next.js frontend.

## 🚀 Quick Start

### Installation
```bash
npm run install:all
```

### Development
```bash
npm run dev
```

This starts both servers:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3002

## 📋 Available Commands

### Development
- `npm run dev` - Start both servers
- `npm run dev:frontend` - Start frontend only
- `npm run dev:backend` - Start backend only

### Setup & Installation
- `npm run install:all` - Install all dependencies
- `npm run setup` - Setup both projects
- `npm run setup:frontend` - Setup frontend
- `npm run setup:backend` - Setup backend

### Building
- `npm run build` - Build both for production
- `npm run build:frontend` - Build frontend
- `npm run build:backend` - Check backend

### Database
- `npm run migrate` - Run migrations
- `npm run migrate:create` - Create migrations

### Testing
- `npm run test` - Test both
- `npm run test:backend` - Test backend
- `npm run test:frontend` - Test frontend

### Deployment
- `npm run deploy:production` - Deploy to production
- `npm run production` - Run production build

## 🎯 Demo Credentials

### Customer
- Email: `customer@greenwells.com`
- Password: `customer123`

### Driver
- Email: `driver@greenwells.com`
- Password: `driver123`

### Dispatcher
- Email: `dispatcher@greenwells.com`
- Password: `dispatcher123`

### Admin
- Email: `admin@greenwells.com`
- Password: `admin123`

## 📚 Documentation

- [Frontend-Backend Connection Guide](./FRONTEND_BACKEND_CONNECTION.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Backend API Docs](./backend/CYLINDER_API_DOCUMENTATION.md)

## 🏗️ Project Structure

```
greenwells/
├── backend/              # Django backend
│   ├── users/            # User management
│   ├── orders/           # Order management
│   └── backend/          # Django settings
├── main-frontend/        # Next.js frontend
│   ├── app/              # App router
│   ├── components/       # React components
│   └── lib/              # Utilities
└── package.json          # Root package.json
```

## 🔧 Features

- ✅ User Authentication (JWT)
- ✅ Role-based Access Control
- ✅ Order Management
- ✅ Real-time Delivery Tracking
- ✅ Cylinder Management
- ✅ Driver Dashboard
- ✅ Dispatcher Dashboard
- ✅ Customer Dashboard

## 🌐 Tech Stack

### Backend
- Django 5.2
- Django REST Framework
- JWT Authentication
- SQLite (Development)

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Radix UI Components

## 📞 Support

For issues or questions, please open an issue on GitHub.

## 📝 License

MIT License - see LICENSE file for details.
