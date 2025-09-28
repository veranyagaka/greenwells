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

export async function POST(request: NextRequest) {
  try {
    const user = await authenticateUser(request);
    
    if (!user) {
      return NextResponse.json(
        { success: false, message: 'Authentication required' },
        { status: 401 }
      );
    }

    // Only drivers can submit GPS logs
    if (user.role !== 'driver') {
      return NextResponse.json(
        { success: false, message: 'Only drivers can submit GPS logs' },
        { status: 403 }
      );
    }

    const { latitude, longitude, notes, orderId, vehicleId } = await request.json();

    // Validate GPS coordinates
    if (!latitude || !longitude || 
        latitude < -90 || latitude > 90 || 
        longitude < -180 || longitude > 180) {
      return NextResponse.json(
        { success: false, message: 'Valid latitude and longitude are required' },
        { status: 400 }
      );
    }

    // Get driver information
    // const driver = await prisma.driver.findUnique({
    //   where: { userId: user.userId },
    //   include: { assignedVehicle: true, currentOrder: true }
    // });

    // Mock driver data - replace with actual database query
    const driver = {
      id: 'DRV-001',
      userId: user.userId,
      name: user.email.split('@')[0],
      currentOrderId: orderId,
      assignedVehicleId: vehicleId || 'VEH-001',
    };

    if (!driver) {
      return NextResponse.json(
        { success: false, message: 'Driver profile not found' },
        { status: 404 }
      );
    }

    // Create GPS log entry
    // const gpsLog = await prisma.gPSLog.create({
    //   data: {
    //     driverId: driver.id,
    //     vehicleId: vehicleId || driver.assignedVehicleId,
    //     orderId: orderId || driver.currentOrderId,
    //     location: {
    //       latitude: parseFloat(latitude),
    //       longitude: parseFloat(longitude),
    //       timestamp: new Date().toISOString(),
    //     },
    //     notes: notes || null,
    //     timestamp: new Date(),
    //   }
    // });

    // Mock GPS log - replace with actual database operation
    const gpsLog = {
      id: `GPS-${Date.now()}`,
      driverId: driver.id,
      vehicleId: vehicleId || driver.assignedVehicleId,
      orderId: orderId || driver.currentOrderId,
      location: {
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        timestamp: new Date().toISOString(),
      },
      notes: notes || null,
      timestamp: new Date().toISOString(),
    };

    // Update driver's current location
    // await prisma.driver.update({
    //   where: { id: driver.id },
    //   data: {
    //     location: {
    //       latitude: parseFloat(latitude),
    //       longitude: parseFloat(longitude),
    //       timestamp: new Date().toISOString(),
    //     },
    //     lastActiveAt: new Date(),
    //   }
    // });

    // Real-time updates via WebSocket (would need separate WebSocket server)
    const locationUpdate = {
      type: 'location_update',
      payload: {
        driverId: driver.id,
        orderId: orderId || driver.currentOrderId,
        vehicleId: vehicleId || driver.assignedVehicleId,
        location: {
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
        },
        timestamp: new Date().toISOString(),
      }
    };

    // In a real application, you would broadcast this to connected WebSocket clients
    console.log('Broadcasting location update:', locationUpdate);

    // Update order status if applicable
    if (orderId) {
      // await prisma.order.update({
      //   where: { id: orderId },
      //   data: {
      //     lastLocationUpdate: new Date(),
      //   }
      // });

      // Notify customer about location update
      // await sendCustomerNotification(orderId, 'location_update', gpsLog);
    }

    return NextResponse.json({
      success: true,
      data: { gpsLog },
      message: 'GPS location updated successfully'
    }, { status: 201 });

  } catch (error) {
    console.error('GPS update error:', error);
    return NextResponse.json(
      { success: false, message: 'Failed to update GPS location' },
      { status: 500 }
    );
  }
}

// GET endpoint to retrieve GPS logs
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
    const orderId = searchParams.get('orderId');
    const driverId = searchParams.get('driverId');
    const vehicleId = searchParams.get('vehicleId');

    // Build query filters based on user role and parameters
    let whereClause: any = {};

    if (user.role === 'driver') {
      // Drivers can only see their own GPS logs
      whereClause.driverId = `DRV-${user.userId}`;
    }

    if (orderId) whereClause.orderId = orderId;
    if (driverId) whereClause.driverId = driverId;
    if (vehicleId) whereClause.vehicleId = vehicleId;

    // Fetch GPS logs from database
    // const gpsLogs = await prisma.gPSLog.findMany({
    //   where: whereClause,
    //   orderBy: { timestamp: 'desc' },
    //   take: 50, // Limit to last 50 entries
    //   include: {
    //     driver: { select: { name: true } },
    //     vehicle: { select: { number: true } },
    //     order: { select: { id: true, status: true } }
    //   }
    // });

    // Mock GPS logs - replace with actual database query
    const mockGpsLogs = [
      {
        id: 'GPS-001',
        driverId: 'DRV-001',
        vehicleId: 'VEH-001',
        orderId: 'ORD-001',
        location: {
          latitude: -1.2921,
          longitude: 36.8219,
          timestamp: new Date().toISOString(),
        },
        notes: 'En route to delivery location',
        timestamp: new Date().toISOString(),
        driver: { name: 'Mike Driver' },
        vehicle: { number: 'KBA 123A' },
        order: { id: 'ORD-001', status: 'ON_ROUTE' }
      }
    ];

    return NextResponse.json({
      success: true,
      data: { gpsLogs: mockGpsLogs }
    });

  } catch (error) {
    console.error('Get GPS logs error:', error);
    return NextResponse.json(
      { success: false, message: 'Failed to fetch GPS logs' },
      { status: 500 }
    );
  }
}