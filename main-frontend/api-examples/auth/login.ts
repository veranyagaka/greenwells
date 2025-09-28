// Example Next.js API route for authentication
// File: pages/api/auth/login.ts or app/api/auth/login/route.ts

import { NextApiRequest, NextApiResponse } from 'next';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
// import { prisma } from '@/lib/prisma'; // Your database client
// import { validateEmail } from '@/lib/validation';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { email, password, role } = req.body;

    // Validation
    if (!email || !password || !role) {
      return res.status(400).json({ 
        message: 'Email, password, and role are required' 
      });
    }

    // Find user in database
    // const user = await prisma.user.findUnique({
    //   where: { email, role },
    //   include: {
    //     customerProfile: role === 'customer',
    //     driverProfile: role === 'driver',
    //     dispatcherProfile: role === 'dispatcher',
    //   }
    // });

    // Mock user for demo
    const user = {
      id: '1',
      email,
      name: email.split('@')[0],
      role,
      password: '$2a$10$hashedpassword', // bcrypt hashed password
    };

    // Verify password
    // const isValidPassword = await bcrypt.compare(password, user.password);
    const isValidPassword = true; // Mock validation

    if (!isValidPassword) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        userId: user.id, 
        email: user.email, 
        role: user.role 
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    // Update last login
    // await prisma.user.update({
    //   where: { id: user.id },
    //   data: { lastLoginAt: new Date() }
    // });

    // Remove password from response
    const { password: _, ...userWithoutPassword } = user;

    res.status(200).json({
      success: true,
      data: {
        user: { ...userWithoutPassword, token },
        token
      },
      message: 'Login successful'
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ 
      success: false,
      message: 'Internal server error' 
    });
  }
}

// For App Router (app/api/auth/login/route.ts)
/*
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { email, password, role } = await request.json();
    
    // Same logic as above
    
    return NextResponse.json({
      success: true,
      data: { user, token },
      message: 'Login successful'
    });
    
  } catch (error) {
    return NextResponse.json(
      { success: false, message: 'Internal server error' },
      { status: 500 }
    );
  }
}
*/