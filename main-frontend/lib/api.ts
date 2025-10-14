// API utility functions for Django REST Framework integration
// This file provides a structure for seamless integration with Django backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

// Auth token management
export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  const user = localStorage.getItem('ugunja_user');
  if (user) {
    try {
      const parsedUser = JSON.parse(user);
      return parsedUser.token;
    } catch {
      return null;
    }
  }
  return null;
};

// Base API fetch wrapper with authentication
export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const token = getAuthToken();
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'An error occurred' }));
    throw new Error(error.message || 'API request failed');
  }

  return response.json();
};

// Authentication API calls
export const authAPI = {
  login: async (credentials: { email: string; password: string; role: string }) => {
    return apiRequest<{ user: any; token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  register: async (userData: { name: string; email: string; password: string; role: string }) => {
    return apiRequest<{ user: any; token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  logout: async () => {
    return apiRequest('/auth/logout', { method: 'POST' });
  },

  refreshToken: async () => {
    return apiRequest<{ token: string }>('/auth/refresh', { method: 'POST' });
  },
};

// Orders API calls
export const ordersAPI = {
  getOrders: async (params?: { status?: string; page?: number; limit?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    
    const query = queryParams.toString();
    return apiRequest<{ orders: any[]; total: number; page: number }>(`/orders${query ? `?${query}` : ''}`);
  },

  createOrder: async (orderData: any) => {
    return apiRequest<{ order: any }>('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  },

  updateOrder: async (orderId: string, updates: any) => {
    return apiRequest<{ order: any }>(`/orders/${orderId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  },

  deleteOrder: async (orderId: string) => {
    return apiRequest(`/orders/${orderId}`, { method: 'DELETE' });
  },
};

// Vehicles API calls
export const vehiclesAPI = {
  getVehicles: async () => {
    return apiRequest<{ vehicles: any[] }>('/vehicles');
  },

  createVehicle: async (vehicleData: any) => {
    return apiRequest<{ vehicle: any }>('/vehicles', {
      method: 'POST',
      body: JSON.stringify(vehicleData),
    });
  },

  updateVehicle: async (vehicleId: string, updates: any) => {
    return apiRequest<{ vehicle: any }>(`/vehicles/${vehicleId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  },

  deleteVehicle: async (vehicleId: string) => {
    return apiRequest(`/vehicles/${vehicleId}`, { method: 'DELETE' });
  },
};

// Drivers API calls
export const driversAPI = {
  getDrivers: async () => {
    return apiRequest<{ drivers: any[] }>('/drivers');
  },

  createDriver: async (driverData: any) => {
    return apiRequest<{ driver: any }>('/drivers', {
      method: 'POST',
      body: JSON.stringify(driverData),
    });
  },

  updateDriver: async (driverId: string, updates: any) => {
    return apiRequest<{ driver: any }>(`/drivers/${driverId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  },

  updateDriverLocation: async (driverId: string, location: { latitude: number; longitude: number; notes?: string }) => {
    return apiRequest(`/drivers/${driverId}/location`, {
      method: 'POST',
      body: JSON.stringify(location),
    });
  },
};

// Tracking API calls
export const trackingAPI = {
  getActiveDeliveries: async () => {
    return apiRequest<{ deliveries: any[] }>('/tracking/active');
  },

  updateDeliveryStatus: async (deliveryId: string, status: string, location?: { latitude: number; longitude: number }) => {
    return apiRequest(`/tracking/${deliveryId}/status`, {
      method: 'POST',
      body: JSON.stringify({ status, location }),
    });
  },

  submitGPSLog: async (deliveryId: string, location: { latitude: number; longitude: number; notes?: string }) => {
    return apiRequest(`/tracking/${deliveryId}/gps`, {
      method: 'POST',
      body: JSON.stringify(location),
    });
  },
};

// Assignment API calls
export const assignmentAPI = {
  assignOrder: async (orderId: string, driverId: string, vehicleId: string) => {
    return apiRequest('/assignments', {
      method: 'POST',
      body: JSON.stringify({ orderId, driverId, vehicleId }),
    });
  },

  autoAssignOrder: async (orderId: string) => {
    return apiRequest('/assignments/auto', {
      method: 'POST',
      body: JSON.stringify({ orderId }),
    });
  },
};

// Analytics API calls
export const analyticsAPI = {
  getDashboardStats: async (role: string) => {
    return apiRequest<{ stats: any }>(`/analytics/dashboard?role=${role}`);
  },

  getPerformanceMetrics: async (timeRange: string) => {
    return apiRequest<{ metrics: any }>(`/analytics/performance?range=${timeRange}`);
  },
};

// Real-time WebSocket connection helper for Django Channels
export const createWebSocketConnection = (path: string, token?: string) => {
  const wsUrl = `${WS_BASE_URL}${path}${token ? `?token=${token}` : ''}`;
  
  return new WebSocket(wsUrl);
};

// Django-specific WebSocket helpers
export const createTrackingWebSocket = (orderId: string, token?: string) => {
  return createWebSocketConnection(`/tracking/${orderId}/`, token);
};

export const createDriverLocationWebSocket = (driverId: string, token?: string) => {
  return createWebSocketConnection(`/driver/${driverId}/location/`, token);
};

// Error handling utility
export const handleAPIError = (error: any) => {
  console.error('API Error:', error);
  
  if (error.message === 'Unauthorized' || error.status === 401) {
    // Handle token expiration
    localStorage.removeItem('ugunja_user');
    window.location.href = '/';
  }
  
  return error.message || 'An unexpected error occurred';
};

// Data validation utilities
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
  return phoneRegex.test(phone) && phone.length >= 10;
};

export const validateCoordinates = (lat: number, lng: number): boolean => {
  return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
};

// ============= CYLINDER API CALLS =============

export const cylinderAPI = {
  /**
   * Register a new cylinder with QR/RFID codes
   * Only dispatchers and admins can register cylinders
   */
  registerCylinder: async (data: any) => {
    return apiRequest<any>('/cylinders/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Scan and verify cylinder authenticity using QR or RFID code
   * Available to all authenticated users
   */
  scanCylinder: async (data: any) => {
    return apiRequest<any>('/cylinders/scan/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get list of cylinders (filtered by user role)
   */
  getCylinders: async (params?: {
    status?: string;
    cylinderType?: string;
    isTampered?: boolean;
    isExpired?: boolean;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.cylinderType) queryParams.append('cylinder_type', params.cylinderType);
    if (params?.isTampered !== undefined) queryParams.append('is_tampered', params.isTampered.toString());
    if (params?.isExpired !== undefined) queryParams.append('is_expired', params.isExpired.toString());
    
    const query = queryParams.toString();
    return apiRequest<{ cylinders: any[] }>(`/cylinders/${query ? `?${query}` : ''}`);
  },

  /**
   * Get specific cylinder details with history
   */
  getCylinder: async (cylinderId: string) => {
    return apiRequest<{
      cylinder: any;
      recent_history: any[];
      recent_scans: any[];
    }>(`/cylinders/${cylinderId}/`);
  },

  /**
   * Get complete history for a cylinder
   */
  getCylinderHistory: async (cylinderId: string, params?: {
    eventType?: string;
    startDate?: string;
    endDate?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.eventType) queryParams.append('event_type', params.eventType);
    if (params?.startDate) queryParams.append('start_date', params.startDate);
    if (params?.endDate) queryParams.append('end_date', params.endDate);
    
    const query = queryParams.toString();
    return apiRequest<{
      cylinder: any;
      history: any[];
      total_events: number;
    }>(`/cylinders/${cylinderId}/history/${query ? `?${query}` : ''}`);
  },

  /**
   * Assign cylinder to order or customer
   * Only dispatchers and admins
   */
  assignCylinder: async (data: any) => {
    return apiRequest<{ cylinder: any }>('/cylinders/assign/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update cylinder status
   * Only dispatchers and admins
   */
  updateCylinderStatus: async (cylinderId: string, data: any) => {
    return apiRequest<{ cylinder: any }>(`/cylinders/${cylinderId}/status/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};