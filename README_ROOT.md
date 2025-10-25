# GreenWells LPG Platform - Root Directory

This is a monorepo containing both the Django backend and Next.js frontend.

## 📁 Project Structure

```
greenwells/
├── backend/              # Django REST API backend
│   ├── users/           # User management app
│   ├── orders/          # Order management app
│   └── backend/         # Django settings
├── main-frontend/        # Next.js frontend application
│   ├── app/             # Next.js App Router
│   ├── components/      # React components
│   └── lib/             # Utilities and API client
└── package.json         # Root project file (orchestration only)
```

## 🚀 Quick Start

### Install All Dependencies
```bash
npm run install:all
```

### Start Development Servers
```bash
npm run dev
```

This starts:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

## 📝 Important Notes

- **Root package.json**: This file is for orchestrating both backend and frontend. It does NOT contain Next.js or React dependencies.
- **Next.js**: Located in `main-frontend/` directory
- **Django**: Located in `backend/` directory

## 🔧 Available Commands

See `main-frontend/package.json` for Next.js commands.
See `backend/manage.py` for Django commands.
Use root commands for running both:

```bash
npm run dev              # Start both servers
npm run build            # Build both for production
npm run migrate          # Run database migrations
npm run test             # Run all tests
```

## 📚 Documentation

- [Frontend Guide](./main-frontend/README.md)
- [Backend Guide](./backend/README.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Documentation](./backend/CYLINDER_API_DOCUMENTATION.md)

## ⚠️ Deployment

For production deployment:
- Deploy Next.js from `main-frontend/` directory
- Deploy Django from `backend/` directory
- Do NOT deploy from root (no Next.js here)
