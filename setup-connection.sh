#!/bin/bash

# GreenWells Frontend-Backend Connection Setup Script
# This script helps you set up and test the connection between frontend and backend

echo "🚀 Setting up GreenWells Frontend-Backend Connection..."

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -f "manage.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All dependencies found"

# Setup backend
echo "🔧 Setting up Django backend..."
cd backend

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser (optional)
echo "👤 Would you like to create a superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

echo "✅ Backend setup complete"

# Setup frontend
echo "🔧 Setting up Next.js frontend..."
cd ../main-frontend

# Install Node dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Copy environment file
if [ ! -f ".env.local" ]; then
    echo "📝 Creating environment file..."
    cp env.local.example .env.local
    echo "✅ Environment file created. Please review .env.local and update if needed."
else
    echo "✅ Environment file already exists"
fi

echo "✅ Frontend setup complete"

# Test connection
echo "🧪 Testing connection..."

# Start backend in background
echo "🚀 Starting Django backend..."
cd ../backend
python manage.py runserver 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Test backend health
echo "🔍 Testing backend health..."
if curl -s http://localhost:8000/api/auth/login/ > /dev/null; then
    echo "✅ Backend is running and accessible"
else
    echo "❌ Backend is not accessible. Please check if it's running on port 8000"
fi

# Start frontend
echo "🚀 Starting Next.js frontend..."
cd ../main-frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 10

# Test frontend
echo "🔍 Testing frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running and accessible"
else
    echo "❌ Frontend is not accessible. Please check if it's running on port 3000"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000/api"
echo "👤 Admin Panel: http://localhost:8000/admin"
echo ""
echo "🛑 To stop the servers, press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📚 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Try registering a new user"
echo "   3. Test the login functionality"
echo "   4. Check the browser console for any errors"
echo ""
echo "🔧 If you encounter issues:"
echo "   - Check that both servers are running"
echo "   - Verify the .env.local file has correct API URLs"
echo "   - Check browser console for CORS errors"
echo "   - Ensure Django CORS settings are properly configured"

# Keep script running
wait
