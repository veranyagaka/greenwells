import { NextRequest, NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

interface User {
  userId: string;
  email: string;
  role: string;
}

// Helper function to extract and verify JWT token
async function authenticateUser(request: NextRequest): Promise<User | null> {
  try {
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.split(' ')[1];

    if (!token) {
      return null;
    }

    const decoded = jwt.verify(
      token, 
      process.env.JWT_SECRET || 'your-secret-key-change-in-production'
    ) as User;
    
    return decoded;
  } catch (error) {
    return null;
  }
}

export async function GET(request: NextRequest) {
  try {
    const user = await authenticateUser(request);
    
    if (!user) {
      return NextResponse.json(
        { success: false, message: 'Authentication required' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const page = Number(searchParams.get('page')) || 1;
    const limit = Number(searchParams.get('limit')) || 10;

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
    //   skip: (page - 1) * limit,
    //   take: limit,
    // });

    // Mock data for demo - replace with actual database queries
    const mockOrders = [
      {
        id: 'ORD-001',
        customerId: user.userId,
        customerName: 'John Doe',
        deliveryAddress: '123 Main St, Nairobi',
        pickupLocation: 'Central Depot',
        quantity: 14.2,
        scheduledTime: new Date().toISOString(),
        status: 'ON_ROUTE',
        priority: 'HIGH',
        createdAt: new Date().toISOString(),
        assignedDriver: { name: 'Mike Driver', phoneNumber: '+254700000001' },
        assignedVehicle: { number: 'KBA 123A', type: 'Truck' },
      },
      {
        id: 'ORD-002',
        customerId: user.userId,
        customerName: 'Jane Smith',
        deliveryAddress: '456 Oak Ave, Mombasa',
        pickupLocation: 'East Branch',
        quantity: 25.0,
        scheduledTime: new Date(Date.now() + 86400000).toISOString(),
        status: 'PENDING',
        priority: 'MEDIUM',
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        assignedDriver: null,
        assignedVehicle: null,
      }
    ];

    // Filter orders based on user role
    let filteredOrders = mockOrders;
    if (user.role === 'customer') {
      filteredOrders = mockOrders.filter(order => order.customerId === user.userId);
    }

    return NextResponse.json({
      success: true,
      data: {
        orders: filteredOrders,
        pagination: {
          page,
          limit,
          total: filteredOrders.length,
          totalPages: Math.ceil(filteredOrders.length / limit),
        }
      }
    });

  } catch (error) {
    console.error('Get orders error:', error);
    return NextResponse.json(
      { success: false, message: 'Failed to fetch orders' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await authenticateUser(request);
    
    if (!user) {
      return NextResponse.json(
        { success: false, message: 'Authentication required' },
        { status: 401 }
      );
    }

    // Only customers can create orders
    if (user.role !== 'customer') {
      return NextResponse.json(
        { success: false, message: 'Only customers can create orders' },
        { status: 403 }
      );
    }

    const orderData = await request.json();

    // Validate order data
    if (!orderData.deliveryAddress || !orderData.quantity || !orderData.scheduledTime) {
      return NextResponse.json(
        { success: false, message: 'Missing required fields: deliveryAddress, quantity, scheduledTime' },
        { status: 400 }
      );
    }

    // Create order in database
    // const order = await prisma.order.create({
    //   data: {
    //     customerId: user.userId,
    //     deliveryAddress: orderData.deliveryAddress,
    //     pickupLocation: orderData.pickupLocation || 'Central Depot',
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

    // Mock order creation - replace with actual database operation
    const order = {
      id: `ORD-${Date.now()}`,
      customerId: user.userId,
      customerName: user.email.split('@')[0],
      deliveryAddress: orderData.deliveryAddress,
      pickupLocation: orderData.pickupLocation || 'Central Depot',
      quantity: parseFloat(orderData.quantity),
      scheduledTime: orderData.scheduledTime,
      contactDetails: orderData.contactDetails,
      specialInstructions: orderData.specialInstructions,
      status: 'PENDING',
      priority: 'MEDIUM',
      createdAt: new Date().toISOString(),
    };

    // Notify dispatchers about new order (WebSocket/Push notification)
    // await notifyDispatchers('new_order', order);

    return NextResponse.json({
      success: true,
      data: { order },
      message: 'Order created successfully'
    }, { status: 201 });

  } catch (error) {
    console.error('Create order error:', error);
    return NextResponse.json(
      { success: false, message: 'Failed to create order' },
      { status: 500 }
    );
  }
}