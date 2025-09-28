import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import jwt from 'jsonwebtoken';

// Define protected routes that require authentication
const protectedRoutes = ['/api/orders', '/api/tracking'];
const publicRoutes = ['/api/auth/login', '/api/auth/register'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Check if route is protected
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    const token = request.headers.get('authorization')?.split(' ')[1];

    if (!token) {
      return new NextResponse(
        JSON.stringify({ success: false, message: 'Authentication required' }),
        { status: 401, headers: { 'content-type': 'application/json' } }
      );
    }

    try {
      // Verify JWT token
      jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key-change-in-production');
      return NextResponse.next();
    } catch (error) {
      return new NextResponse(
        JSON.stringify({ success: false, message: 'Invalid or expired token' }),
        { status: 403, headers: { 'content-type': 'application/json' } }
      );
    }
  }

  return NextResponse.next();
}

// Configure which routes to run middleware on
export const config = {
  matcher: [
    '/api/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};