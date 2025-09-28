// Example Next.js API route for GPS tracking
// File: pages/api/tracking/gps.ts or app/api/tracking/gps/route.ts

import { NextApiRequest, NextApiResponse } from 'next';
import jwt from 'jsonwebtoken';
// import { prisma } from '@/lib/prisma';

interface AuthenticatedRequest extends NextApiRequest {
  user?: {
    userId: string;
    email: string;
    role: string;
  };
}

// WebSocket connections for real-time updates
const activeConnections = new Map();

export default async function handler(
  req: AuthenticatedRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Authenticate token
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Access token required' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key') as any;
    req.user = decoded;
  } catch (error) {
    return res.status(403).json({ message: 'Invalid or expired token' });
  }

  const user = req.user!;

  // Only drivers can submit GPS logs
  if (user.role !== 'driver') {
    return res.status(403).json({
      success: false,
      message: 'Only drivers can submit GPS logs'
    });
  }

  try {
    const { latitude, longitude, notes, orderId, vehicleId } = req.body;

    // Validate GPS coordinates
    if (!latitude || !longitude || 
        latitude < -90 || latitude > 90 || 
        longitude < -180 || longitude > 180) {
      return res.status(400).json({
        success: false,
        message: 'Valid latitude and longitude are required'
      });
    }

    // Get driver information
    // const driver = await prisma.driver.findUnique({
    //   where: { userId: user.userId },
    //   include: { assignedVehicle: true, currentOrder: true }
    // });

    // Mock driver data
    const driver = {
      id: 'DRV-001',
      userId: user.userId,
      name: user.email.split('@')[0],
      currentOrderId: orderId,
      assignedVehicleId: vehicleId,
    };

    if (!driver) {
      return res.status(404).json({
        success: false,
        message: 'Driver profile not found'
      });
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

    // Mock GPS log
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

    // Real-time updates via WebSocket
    broadcastLocationUpdate({
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
    });

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

    res.status(201).json({
      success: true,
      data: { gpsLog },
      message: 'GPS location updated successfully'
    });

  } catch (error) {
    console.error('GPS update error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update GPS location'
    });
  }
}

// Broadcast location updates to connected clients
function broadcastLocationUpdate(message: any) {
  activeConnections.forEach((connection, connectionId) => {
    if (connection.readyState === 1) { // WebSocket.OPEN
      try {
        connection.send(JSON.stringify(message));
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
        activeConnections.delete(connectionId);
      }
    }
  });
}

// WebSocket handler for real-time tracking
export const websocketHandler = (ws: any, req: any) => {
  const connectionId = Date.now().toString();
  activeConnections.set(connectionId, ws);

  ws.on('message', (message: string) => {
    try {
      const data = JSON.parse(message);
      
      // Handle different message types
      switch (data.type) {
        case 'subscribe_to_order':
          // Subscribe to specific order updates
          ws.orderId = data.orderId;
          break;
        case 'subscribe_to_driver':
          // Subscribe to specific driver updates
          ws.driverId = data.driverId;
          break;
        case 'ping':
          // Keep connection alive
          ws.send(JSON.stringify({ type: 'pong' }));
          break;
      }
    } catch (error) {
      console.error('WebSocket message error:', error);
    }
  });

  ws.on('close', () => {
    activeConnections.delete(connectionId);
  });

  ws.on('error', (error: any) => {
    console.error('WebSocket error:', error);
    activeConnections.delete(connectionId);
  });
};

// Customer notification helper
async function sendCustomerNotification(orderId: string, type: string, data: any) {
  // This would integrate with your notification service
  // Examples: Email, SMS, Push notifications, etc.
  
  // const order = await prisma.order.findUnique({
  //   where: { id: orderId },
  //   include: { customer: true }
  // });

  // if (order) {
  //   await sendEmail({
  //     to: order.customer.email,
  //     subject: 'Delivery Update',
  //     template: 'location_update',
  //     data: { order, location: data.location }
  //   });
  // }
}