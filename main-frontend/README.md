# Ugunja - LPG Delivery & Fleet Management Platform

A modern, responsive Next.js application for LPG delivery and fleet management with role-based authentication and real-time tracking capabilities.

## Features

- **Role-Based Authentication**: Support for customers, drivers, and dispatchers
- **Real-Time Tracking**: GPS tracking and live order updates
- **Responsive Design**: Mobile-first approach with oil-energy themed dark UI
- **Fleet Management**: Vehicle and driver assignment system
- **Order Management**: Complete order lifecycle management
- **Analytics Dashboard**: Performance metrics and reporting

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS v4, Shadcn/ui components
- **Authentication**: JWT tokens with role-based access
- **API**: Next.js API routes with middleware
- **Database**: Ready for Prisma/PostgreSQL integration

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd ugunja-lpg-platform
```

2. Install dependencies
```bash
npm install
```

3. Create environment variables
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
JWT_SECRET=your-super-secret-jwt-key-here
DATABASE_URL=your-database-connection-string
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

4. Run the development server
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   │   ├── auth/          # Authentication endpoints
│   │   ├── orders/        # Order management APIs
│   │   └── tracking/      # GPS tracking APIs
│   ├── layout.tsx         # Root layout
│   └── page.tsx          # Home page
├── components/            # React components
│   ├── ui/               # Shadcn/ui components
│   ├── AuthPage.tsx
│   ├── CustomerDashboard.tsx
│   ├── DriverDashboard.tsx
│   ├── DispatcherDashboard.tsx
│   └── LandingPage.tsx
├── lib/                   # Utility libraries
├── styles/               # Global styles
├── types/                # TypeScript type definitions
└── middleware.ts         # Next.js middleware
```

## User Roles

### Customer
- Place LPG delivery orders
- Track order status and delivery location
- View order history
- Manage delivery preferences

### Driver
- View assigned deliveries
- Update delivery status
- Submit GPS location updates
- Navigate to delivery locations

### Dispatcher/Admin
- Manage all orders and assignments
- Assign drivers and vehicles
- Monitor fleet performance
- View analytics and reports

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Orders
- `GET /api/orders` - Get orders (filtered by user role)
- `POST /api/orders` - Create new order (customers only)

### Tracking
- `POST /api/tracking/gps` - Submit GPS location (drivers only)
- `GET /api/tracking/gps` - Get GPS logs

## Environment Variables

Required environment variables:

```env
JWT_SECRET=              # Secret key for JWT token signing
DATABASE_URL=            # Database connection string
NEXT_PUBLIC_API_URL=     # Public API URL for frontend
```

## Database Integration

The application is structured for easy database integration:

1. Install Prisma: `npm install prisma @prisma/client`
2. Initialize Prisma: `npx prisma init`
3. Define your schema in `prisma/schema.prisma`
4. Uncomment database queries in API routes
5. Run migrations: `npx prisma migrate dev`

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Manual Deployment

1. Build the application:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@ugunja.com or create an issue in the repository.