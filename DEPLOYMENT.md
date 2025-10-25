# GreenWells - Deployment Guide

This guide covers deploying the GreenWells LPG delivery platform, including both backend (Django) and frontend (Next.js).

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm run install:all
```

### 2. Run Development Servers
```bash
npm run dev
```

This will start both:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

## 📦 Available Commands

### Setup Commands
```bash
npm run setup              # Setup both frontend and backend
npm run setup:frontend     # Setup frontend only
npm run setup:backend     # Setup backend only
npm run install:all       # Install all dependencies
```

### Development Commands
```bash
npm run dev                # Start both servers in parallel
npm run dev:frontend       # Start frontend only
npm run dev:backend        # Start backend only
```

### Build Commands
```bash
npm run build              # Build both for production
npm run build:frontend     # Build frontend only
npm run build:backend      # Check backend only
```

### Migration Commands
```bash
npm run migrate            # Run database migrations
npm run migrate:create    # Create new migrations
npm run migrate:reset     # Reset database (with backup)
```

### Testing Commands
```bash
npm run test               # Test both
npm run test:backend       # Test backend
npm run test:frontend      # Test frontend
```

### Linting Commands
```bash
npm run lint               # Lint both
npm run lint:backend       # Lint backend
npm run lint:frontend      # Lint frontend
```

### Cleanup Commands
```bash
npm run clean              # Clean all
npm run clean:frontend    # Clean frontend
npm run clean:backend      # Clean backend
```

### Deployment Commands
```bash
npm run deploy:production  # Deploy to production
npm run production         # Run production build
```

## 🌐 Deployment Options

### Option 1: Heroku Deployment

#### Backend (Django on Heroku)

1. **Create Heroku App:**
```bash
heroku create greenwells-backend
```

2. **Configure Environment Variables:**
```bash
heroku config:set DEBUG=True
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com
```

3. **Deploy Backend:**
```bash
git subtree push --prefix backend heroku main
# OR
git push heroku-remote `git subtree split --prefix backend main`:master --force
```

4. **Run Migrations:**
```bash
heroku run python backend/manage.py migrate
npm run heroku:deploy
```

#### Frontend (Next.js on Vercel)

1. **Connect to Vercel:**
```bash
cd main-frontend
vercel
```

2. **Configure Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://greenwells-backend.herokuapp.com/api
NEXT_PUBLIC_BACKEND_URL=https://greenwells-backend.herokuapp.com
```

3. **Deploy:**
```bash
vercel --prod
```

### Option 2: Docker Deployment

1. **Build Docker Images:**
```bash
npm run docker:build
```

2. **Start Containers:**
```bash
npm run docker:up
```

3. **Stop Containers:**
```bash
npm run docker:down
```

4. **View Logs:**
```bash
npm run docker:logs
```

### Option 3: Traditional Server Deployment

#### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

#### Frontend Setup

```bash
cd main-frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start
```

## 🔧 Environment Configuration

### Backend Environment Variables

Create `.env` file in `backend/`:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Frontend Environment Variables

Create `.env.local` in `main-frontend/`:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com
NEXT_PUBLIC_MOCK_API=false
NODE_ENV=production
```

## 📋 Pre-Deployment Checklist

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected (backend)
- [ ] Production build created (frontend)
- [ ] Security settings updated
- [ ] CORS configured correctly
- [ ] SSL certificates installed
- [ ] Backup strategy in place
- [ ] Monitoring configured

## 🐳 Docker Compose Configuration

Create `docker-compose.yml` in root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend:/app
    command: gunicorn backend.wsgi:application --bind 0.0.0.0:8000

  frontend:
    build: ./main-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000/api
    depends_on:
      - backend
```

## 🔐 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Use HTTPS for all connections
- [ ] Set up proper CORS origins
- [ ] Configure database security
- [ ] Set up rate limiting
- [ ] Configure CSRF protection
- [ ] Use environment variables for secrets
- [ ] Set up proper logging
- [ ] Configure firewall rules

## 📊 Monitoring

### Backend Monitoring
- Django Debug Toolbar (development)
- Django Admin interface
- Server logs
- Database performance

### Frontend Monitoring
- Browser console logs
- Network requests
- Performance metrics
- Error tracking (Sentry)

## 🆘 Troubleshooting

### Backend Issues

**Database not found:**
```bash
npm run migrate
```

**Static files missing:**
```bash
cd backend && python manage.py collectstatic --noinput
```

**Port already in use:**
```bash
# Change port in settings
python manage.py runserver 8001
```

### Frontend Issues

**Build fails:**
```bash
npm run clean:frontend
cd main-frontend && npm install && npm run build
```

**API connection issues:**
- Check `.env.local` configuration
- Verify backend is running
- Check CORS settings

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Heroku Python Support](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Vercel Deployment Guide](https://vercel.com/docs)

## 🎯 Production URLs

- **Frontend**: https://greenwells.vercel.app
- **Backend API**: https://greenwells-api.herokuapp.com
- **Admin Panel**: https://greenwells-api.herokuapp.com/admin

## 📞 Support

For deployment issues, please contact:
- Backend Team: backend@greenwells.com
- Frontend Team: frontend@greenwells.com
- DevOps Team: devops@greenwells.com
