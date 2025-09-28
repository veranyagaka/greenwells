// Example Next.js API route for orders management
// File: pages/api/orders/index.ts or app/api/orders/route.ts

import { NextApiRequest, NextApiResponse } from 'next';
import jwt from 'jsonwebtoken';
// import { prisma } from '@/lib/prisma';
// import { validateOrderData } from '@/lib/validation';

interface AuthenticatedRequest extends NextApiRequest {
  user?: {
    userId: string;
    email: string;
    role: string;
  };
}

// Middleware to verify JWT token
const authenticateToken = (req: AuthenticatedRequest, res: NextApiResponse, next: () => void) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Access token required' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key') as any;
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json({ message: 'Invalid or expired token' });
  }
};

export default async function handler(
  req: AuthenticatedRequest,
  res: NextApiResponse
) {
  // Authenticate user
  await new Promise<void>((resolve, reject) => {
    authenticateToken(req, res, () => resolve());
  });

  const { method } = req;
  const user = req.user!;

  switch (method) {
    case 'GET':
      return handleGetOrders(req, res, user);
    case 'POST':
      return handleCreateOrder(req, res, user);
    default:
      res.setHeader('Allow', ['GET', 'POST']);
      return res.status(405).json({ message: `Method ${method} not allowed` });
  }
}

async function handleGetOrders(
  req: AuthenticatedRequest,
  res: NextApiResponse,
  user: any
) {
  try {
    const { status, page = 1, limit = 10 } = req.query;
    const skip = (Number(page) - 1) * Number(limit);

    // Build where clause based on user role
    let whereClause: any = {};

    if (user.role === 'customer') {
      whereClause.customerId = user.userId;
    }

    if (status) {
      whereClause.status = status;
    }

    // Fetch orders from database
    // const orders = await prisma.order.findMany({
    //   where: whereClause,
    //   include: {
    //     customer: { select: { name: true, email: true } },
    //     assignedDriver: { select: { name: true, phoneNumber: true } },
    //     assignedVehicle: { select: { number: true, type: true } },
    //   },
    //   orderBy: { createdAt: 'desc' },
    //   skip,
    //   take: Number(limit),
    // });

    // const total = await prisma.order.count({ where: whereClause });

    // Mock data for demo
    const mockOrders = [
      {
        id: 'ORD-001',
        customerId: user.userId,
        customerName: 'John Doe',
        deliveryAddress: '123 Main St, City',
        pickupLocation: 'Central Depot',
        quantity: 14.2,
        scheduledTime: new Date().toISOString(),
        status: 'ON_ROUTE',
        priority: 'HIGH',
        createdAt: new Date().toISOString(),
      }
    ];

    res.status(200).json({
      success: true,
      data: {
        orders: mockOrders,
        pagination: {
          page: Number(page),
          limit: Number(limit),
          total: mockOrders.length,
          totalPages: Math.ceil(mockOrders.length / Number(limit)),
        }
      }
    });

  } catch (error) {
    console.error('Get orders error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch orders'
    });
  }
}

async function handleCreateOrder(
  req: AuthenticatedRequest,
  res: NextApiResponse,
  user: any
) {
  try {
    // Only customers can create orders
    if (user.role !== 'customer') {
      return res.status(403).json({
        success: false,
        message: 'Only customers can create orders'
      });
    }

    const orderData = req.body;

    // Validate order data
    // const validation = validateOrderData(orderData);
    // if (!validation.isValid) {
    //   return res.status(400).json({
    //     success: false,
    //     message: 'Invalid order data',
    //     errors: validation.errors
    //   });
    // }

    // Create order in database
    // const order = await prisma.order.create({
    //   data: {
    //     customerId: user.userId,
    //     deliveryAddress: orderData.deliveryAddress,
    //     pickupLocation: orderData.pickupLocation,
    //     quantity: parseFloat(orderData.quantity),
    //     scheduledTime: new Date(orderData.scheduledTime),
    //     contactDetails: orderData.contactDetails,
    //     specialInstructions: orderData.specialInstructions,
    //     status: 'PENDING',
    //     priority: 'MEDIUM',
    //   },
    //   include: {
    //     customer: { select: { name: true, email: true } }
    //   }
    // });

    // Mock order creation
    const order = {
      id: `ORD-${Date.now()}`,
      customerId: user.userId,
      customerName: user.email.split('@')[0],
      ...orderData,
      quantity: parseFloat(orderData.quantity),
      status: 'PENDING',
      priority: 'MEDIUM',
      createdAt: new Date().toISOString(),
    };

    // Notify dispatchers about new order (WebSocket/Push notification)
    // await notifyDispatchers('new_order', order);

    res.status(201).json({
      success: true,
      data: { order },
      message: 'Order created successfully'
    });

  } catch (error) {
    console.error('Create order error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create order'
    });
  }
}

// For App Router (app/api/orders/route.ts)
/*
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  // Extract user from JWT token
  // Same logic as handleGetOrders
}

export async function POST(request: NextRequest) {
  // Same logic as handleCreateOrder
}
*/