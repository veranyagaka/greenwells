// Type definitions for Ugunja LPG Fleet Management System

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'customer' | 'driver' | 'dispatcher';
  token: string;
  phoneNumber?: string;
  address?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Order {
  id: string;
  customerId: string;
  customerName: string;
  deliveryAddress: string;
  pickupLocation: string;
  quantity: number; // in kg
  scheduledTime: string;
  contactDetails: string;
  specialInstructions?: string;
  status: OrderStatus;
  priority: OrderPriority;
  assignedDriverId?: string;
  assignedVehicleId?: string;
  estimatedArrival?: string;
  actualDeliveryTime?: string;
  totalCost?: number;
  createdAt: string;
  updatedAt: string;
}

export type OrderStatus = 'PENDING' | 'ASSIGNED' | 'ON_ROUTE' | 'DELIVERED' | 'CANCELLED';
export type OrderPriority = 'HIGH' | 'MEDIUM' | 'LOW';

export interface Vehicle {
  id: string;
  number: string;
  type: 'TRUCK' | 'VAN' | 'TRAILER';
  capacity: number; // in kg
  currentLoad: number; // in kg
  status: VehicleStatus;
  assignedDriverId?: string;
  lastServiceDate: string;
  nextServiceDate?: string;
  fuelLevel: number; // percentage
  location: GPSLocation;
  licensePlate: string;
  model?: string;
  year?: number;
  createdAt: string;
  updatedAt: string;
}

export type VehicleStatus = 'AVAILABLE' | 'ASSIGNED' | 'MAINTENANCE' | 'OUT_OF_SERVICE';

export interface Driver {
  id: string;
  userId: string;
  name: string;
  phoneNumber: string;
  email: string;
  licenseNumber: string;
  licenseExpiryDate: string;
  status: DriverStatus;
  assignedVehicleId?: string;
  currentOrderId?: string;
  rating: number;
  totalDeliveries: number;
  location: GPSLocation;
  isOnline: boolean;
  lastActiveAt: string;
  createdAt: string;
  updatedAt: string;
}

export type DriverStatus = 'ONLINE' | 'OFFLINE' | 'ON_DELIVERY' | 'BREAK';

export interface GPSLocation {
  latitude: number;
  longitude: number;
  address?: string;
  timestamp?: string;
}

export interface Delivery {
  id: string;
  orderId: string;
  driverId: string;
  vehicleId: string;
  status: DeliveryStatus;
  startTime?: string;
  endTime?: string;
  route: GPSLocation[];
  distanceTraveled?: number; // in km
  estimatedDuration?: number; // in minutes
  actualDuration?: number; // in minutes
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export type DeliveryStatus = 'ASSIGNED' | 'ON_ROUTE' | 'DELIVERED' | 'CANCELLED';

export interface GPSLog {
  id: string;
  driverId: string;
  vehicleId?: string;
  orderId?: string;
  location: GPSLocation;
  speed?: number; // km/h
  heading?: number; // degrees
  accuracy?: number; // meters
  notes?: string;
  timestamp: string;
}

export interface Assignment {
  id: string;
  orderId: string;
  driverId: string;
  vehicleId: string;
  assignedBy: string; // dispatcher user ID
  assignedAt: string;
  status: AssignmentStatus;
  estimatedDistance?: number; // in km
  estimatedDuration?: number; // in minutes
  actualDistance?: number;
  actualDuration?: number;
  notes?: string;
}

export type AssignmentStatus = 'ACTIVE' | 'COMPLETED' | 'CANCELLED';

export interface DashboardStats {
  totalOrders: number;
  activeDeliveries: number;
  completedToday: number;
  totalRevenue?: number;
  availableVehicles: number;
  onlineDrivers: number;
  avgDeliveryTime?: number;
  customerSatisfaction?: number;
}

export interface PerformanceMetrics {
  deliverySuccessRate: number;
  averageDeliveryTime: number;
  fuelEfficiency: number;
  driverRatings: number;
  vehicleUtilization: number;
  routeOptimization: number;
  timeRange: string;
}

export interface NotificationSettings {
  orderUpdates: boolean;
  deliveryAlerts: boolean;
  maintenanceReminders: boolean;
  performanceReports: boolean;
  emailNotifications: boolean;
  smsNotifications: boolean;
  pushNotifications: boolean;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: string[];
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface WebSocketMessage {
  type: 'location_update' | 'status_change' | 'new_order' | 'order_update' | 'driver_status' | 'vehicle_status';
  payload: any;
  timestamp: string;
}

export interface RouteOptimization {
  orderId: string;
  estimatedRoute: GPSLocation[];
  estimatedDistance: number; // km
  estimatedDuration: number; // minutes
  trafficConditions?: 'LOW' | 'MEDIUM' | 'HIGH';
  suggestedDepartureTime?: string;
  alternativeRoutes?: RouteOptimization[];
}

export interface ComplianceRecord {
  id: string;
  vehicleId: string;
  driverId: string;
  type: 'SAFETY_CHECK' | 'INSPECTION' | 'MAINTENANCE' | 'TRAINING';
  status: 'COMPLIANT' | 'NON_COMPLIANT' | 'PENDING';
  details: string;
  dueDate?: string;
  completedDate?: string;
  inspector?: string;
  documents?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface EmergencyContact {
  id: string;
  name: string;
  relationship: string;
  phoneNumber: string;
  email?: string;
  isPrimary: boolean;
}

export interface CustomerProfile extends User {
  companyName?: string;
  billingAddress?: string;
  preferredDeliveryTime?: string;
  specialRequirements?: string;
  emergencyContacts: EmergencyContact[];
  creditLimit?: number;
  currentBalance?: number;
}

export interface DriverProfile extends User {
  licenseDetails: {
    number: string;
    type: string;
    expiryDate: string;
    issuingAuthority: string;
  };
  emergencyContacts: EmergencyContact[];
  medicalClearance?: {
    expiryDate: string;
    issuingDoctor: string;
  };
  trainingRecords: {
    type: string;
    completedDate: string;
    expiryDate?: string;
    certificate?: string;
  }[];
}

export interface DispatcherProfile extends User {
  permissions: {
    canAssignOrders: boolean;
    canManageVehicles: boolean;
    canManageDrivers: boolean;
    canViewAnalytics: boolean;
    canModifyPricing: boolean;
  };
  supervisorId?: string;
}

// Form types for UI components
export interface OrderFormData {
  deliveryAddress: string;
  pickupLocation: string;
  quantity: string;
  scheduledTime: string;
  contactDetails: string;
  specialInstructions: string;
}

export interface VehicleFormData {
  number: string;
  type: string;
  capacity: string;
  licensePlate: string;
  model?: string;
  year?: string;
}

export interface DriverFormData {
  name: string;
  email: string;
  phoneNumber: string;
  licenseNumber: string;
  licenseExpiryDate: string;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  phoneNumber?: string;
  companyName?: string;
}