import { NextRequest, NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';

export async function POST(request: NextRequest) {
  try {
    const { email, password, role } = await request.json();

    // Validation
    if (!email || !password || !role) {
      return NextResponse.json(
        { 
          success: false,
          message: 'Email, password, and role are required' 
        },
        { status: 400 }
      );
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

    // Mock user for demo - replace with actual database query
    const user = {
      id: `${role}_${Date.now()}`,
      email,
      name: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
      role,
      password: '$2a$10$hashedpassword', // bcrypt hashed password
    };

    // Verify password
    // const isValidPassword = await bcrypt.compare(password, user.password);
    const isValidPassword = true; // Mock validation - replace with actual password check

    if (!isValidPassword) {
      return NextResponse.json(
        { 
          success: false,
          message: 'Invalid credentials' 
        },
        { status: 401 }
      );
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        userId: user.id, 
        email: user.email, 
        role: user.role 
      },
      process.env.JWT_SECRET || 'your-secret-key-change-in-production',
      { expiresIn: '24h' }
    );

    // Update last login
    // await prisma.user.update({
    //   where: { id: user.id },
    //   data: { lastLoginAt: new Date() }
    // });

    // Remove password from response
    const { password: _, ...userWithoutPassword } = user;

    return NextResponse.json({
      success: true,
      data: {
        user: { ...userWithoutPassword, token },
        token
      },
      message: 'Login successful'
    });

  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { 
        success: false,
        message: 'Internal server error' 
      },
      { status: 500 }
    );
  }
}