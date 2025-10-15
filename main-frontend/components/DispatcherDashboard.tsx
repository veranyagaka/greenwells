import React, { useState } from 'react';
import AnalyticsPanel from './ui/analytics';
import LiveMap from './ui/livemap';
import { fetchDrivers } from '@/lib/api';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';

import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Textarea } from './ui/textarea';
import { 
  Flame, 
  Plus, 
  Edit, 
  Trash2, 
  MapPin, 
  Users, 
  Truck, 
  Package, 
  LogOut, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  BarChart3,
  TrendingUp,
  Activity,
  Phone,
  Navigation,
  Settings,
  UserCheck
} from 'lucide-react';

interface User {
  id: string;
  email: string;
  role: string;
  name: string;
  token: string;
}

interface DispatcherDashboardProps {
  user: User;
  onLogout: () => void;
}

type OrderStatus = 'PENDING' | 'ASSIGNED' | 'ON_ROUTE' | 'DELIVERED' | 'CANCELLED';
type VehicleStatus = 'AVAILABLE' | 'ASSIGNED' | 'MAINTENANCE' | 'OUT_OF_SERVICE';
type DriverStatus = 'ONLINE' | 'OFFLINE' | 'ON_DELIVERY' | 'BREAK';

interface Order {
  id: string;
  customerName: string;
  deliveryAddress: string;
  quantity: number;
  scheduledTime: string;
  status: OrderStatus;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  assignedDriverId?: string;
  assignedVehicleId?: string;
  createdAt: string;
}

interface Vehicle {
  id: string;
  number: string;
  capacity: number;
  currentLoad: number;
  status: VehicleStatus;
  assignedDriverId?: string;
  lastService: string;
  fuelLevel: number;
  location: string;
}

interface Driver {
  id: string;
  name: string;
  phone: string;
  status: DriverStatus;
  assignedVehicleId?: string;
  currentOrderId?: string;
  rating: number;
  totalDeliveries: number;
  location: string;
}

export function DispatcherDashboard({ user, onLogout }: DispatcherDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [isVehicleDialogOpen, setIsVehicleDialogOpen] = useState(false);
  const [isAssignDialogOpen, setIsAssignDialogOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  // Mock data
  const [orders, setOrders] = useState<Order[]>([
    {
      id: 'ORD-001',
      customerName: 'Sarah Johnson',
      deliveryAddress: '123 Main St, Downtown City',
      quantity: 14.2,
      scheduledTime: '2024-01-15T10:00',
      status: 'ON_ROUTE',
      priority: 'HIGH',
      assignedDriverId: 'DRV-001',
      assignedVehicleId: 'VEH-001',
      createdAt: '2024-01-14T08:30'
    },
    {
      id: 'ORD-002',
      customerName: 'Robert Chen',
      deliveryAddress: '456 Oak Avenue, Suburb Area',
      quantity: 9.5,
      scheduledTime: '2024-01-15T14:00',
      status: 'ASSIGNED',
      priority: 'MEDIUM',
      assignedDriverId: 'DRV-002',
      assignedVehicleId: 'VEH-002',
      createdAt: '2024-01-14T12:15'
    },
    {
      id: 'ORD-003',
      customerName: 'Emily Davis',
      deliveryAddress: '789 Pine Street, East District',
      quantity: 12.0,
      scheduledTime: '2024-01-15T16:00',
      status: 'PENDING',
      priority: 'MEDIUM',
      createdAt: '2024-01-15T09:00'
    }
  ]);

  const [vehicles, setVehicles] = useState<Vehicle[]>([
    {
      id: 'VEH-001',
      number: 'LPG-001',
      capacity: 500,
      currentLoad: 23.7,
      status: 'ASSIGNED',
      assignedDriverId: 'DRV-001',
      lastService: '2023-12-15',
      fuelLevel: 85,
      location: 'Downtown Route'
    },
    {
      id: 'VEH-002',
      number: 'LPG-002',
      capacity: 500,
      currentLoad: 9.5,
      status: 'ASSIGNED',
      assignedDriverId: 'DRV-002',
      lastService: '2023-12-10',
      fuelLevel: 92,
      location: 'Suburb Area'
    },
    {
      id: 'VEH-003',
      number: 'LPG-003',
      capacity: 750,
      currentLoad: 0,
      status: 'AVAILABLE',
      lastService: '2023-12-20',
      fuelLevel: 78,
      location: 'Central Depot'
    }
  ]);

  const [drivers, setDrivers] = useState<Driver[]>([
    {
      id: 'DRV-001',
      name: 'John Smith',
      phone: '+1 234-567-8900',
      status: 'ON_DELIVERY',
      assignedVehicleId: 'VEH-001',
      currentOrderId: 'ORD-001',
      rating: 4.8,
      totalDeliveries: 287,
      location: 'Downtown City'
    },
    {
      id: 'DRV-002',
      name: 'Mike Johnson',
      phone: '+1 234-567-8901',
      status: 'ONLINE',
      assignedVehicleId: 'VEH-002',
      currentOrderId: 'ORD-002',
      rating: 4.6,
      totalDeliveries: 213,
      location: 'Suburb Area'
    },
    {
      id: 'DRV-003',
      name: 'David Wilson',
      phone: '+1 234-567-8902',
      status: 'ONLINE',
      rating: 4.9,
      totalDeliveries: 156,
      location: 'Central Depot'
    }
  ]);

  const [newVehicle, setNewVehicle] = useState({
    number: '',
    capacity: '',
    status: 'AVAILABLE' as VehicleStatus
  });

  const handleCreateVehicle = (e: React.FormEvent) => {
    e.preventDefault();
    const vehicle: Vehicle = {
      id: `VEH-${String(vehicles.length + 1).padStart(3, '0')}`,
      number: newVehicle.number,
      capacity: parseInt(newVehicle.capacity),
      currentLoad: 0,
      status: newVehicle.status,
      lastService: new Date().toISOString().split('T')[0],
      fuelLevel: 100,
      location: 'Central Depot'
    };
    
    setVehicles([...vehicles, vehicle]);
    setNewVehicle({ number: '', capacity: '', status: 'AVAILABLE' });
    setIsVehicleDialogOpen(false);
  };

  const handleAssignOrder = (e: React.FormEvent) => {
    e.preventDefault();
    // Assignment logic would go here
    setIsAssignDialogOpen(false);
    setSelectedOrder(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'ASSIGNED': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'ON_ROUTE': return 'bg-primary/20 text-primary border-primary/30';
      case 'DELIVERED': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'CANCELLED': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'AVAILABLE': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'MAINTENANCE': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'OUT_OF_SERVICE': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'ONLINE': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'OFFLINE': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      case 'ON_DELIVERY': return 'bg-primary/20 text-primary border-primary/30';
      case 'BREAK': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-muted';
    }
  };

  const statsData = {
    totalOrders: orders.length,
    activeDeliveries: orders.filter(o => ['ASSIGNED', 'ON_ROUTE'].includes(o.status)).length,
    availableVehicles: vehicles.filter(v => v.status === 'AVAILABLE').length,
    onlineDrivers: drivers.filter(d => ['ONLINE', 'ON_DELIVERY'].includes(d.status)).length
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 md:gap-3">
              <div className="relative">
                <BarChart3 className="w-6 h-6 md:w-8 md:h-8 text-primary" />
                <div className="absolute inset-0 w-6 h-6 md:w-8 md:h-8 bg-primary/20 rounded-full blur-lg"></div>
              </div>
              <div>
                <h1 className="text-lg md:text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Ugunja Dispatch
                </h1>
                <p className="text-xs md:text-sm text-muted-foreground">Fleet Control - {user.name}</p>
              </div>
            </div>
            <Button variant="outline" onClick={onLogout} className="border-border/50 text-xs md:text-sm px-2 md:px-4">
              <LogOut className="w-3 h-3 md:w-4 md:h-4 md:mr-2" />
              <span className="hidden md:inline">Logout</span>
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-4 md:py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6 mb-6 md:mb-8">
          <Card className="border-border/50 bg-gradient-to-br from-card to-primary/5">
            <CardContent className="p-3 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">Total Orders</p>
                  <p className="text-xl md:text-3xl font-bold">{statsData.totalOrders}</p>
                  <p className="text-xs text-green-400 flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3" />
                    <span className="hidden md:inline">+12% today</span>
                    <span className="md:hidden">+12%</span>
                  </p>
                </div>
                <Package className="w-6 h-6 md:w-10 md:h-10 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-accent/5">
            <CardContent className="p-3 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">Active Deliveries</p>
                  <p className="text-xl md:text-3xl font-bold">{statsData.activeDeliveries}</p>
                  <p className="text-xs text-primary flex items-center gap-1 mt-1">
                    <Activity className="w-3 h-3" />
                    <span className="hidden md:inline">Live tracking</span>
                    <span className="md:hidden">Live</span>
                  </p>
                </div>
                <Truck className="w-6 h-6 md:w-10 md:h-10 text-accent" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-primary/5">
            <CardContent className="p-3 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">Available Vehicles</p>
                  <p className="text-xl md:text-3xl font-bold">{statsData.availableVehicles}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    <span className="hidden md:inline">{vehicles.length} total fleet</span>
                    <span className="md:hidden">{vehicles.length} total</span>
                  </p>
                </div>
                <Truck className="w-6 h-6 md:w-10 md:h-10 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-accent/5">
            <CardContent className="p-3 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">Online Drivers</p>
                  <p className="text-xl md:text-3xl font-bold">{statsData.onlineDrivers}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    <span className="hidden md:inline">{drivers.length} total drivers</span>
                    <span className="md:hidden">{drivers.length} total</span>
                  </p>
                </div>
                <Users className="w-6 h-6 md:w-10 md:h-10 text-accent" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="flex flex-col gap-2 mb-6 md:mb-8">
            {/* Primary tabs for mobile, all tabs for desktop */}
            <TabsList className="grid w-full grid-cols-3 md:grid-cols-5 h-auto">
              <TabsTrigger value="overview" className="text-xs md:text-sm py-2">Overview</TabsTrigger>
              <TabsTrigger value="orders" className="text-xs md:text-sm py-2">Orders</TabsTrigger>
              <TabsTrigger value="tracking" className="text-xs md:text-sm py-2">Track</TabsTrigger>
              <TabsTrigger value="vehicles" className="hidden md:block text-sm py-2">Vehicles</TabsTrigger>
              <TabsTrigger value="drivers" className="hidden md:block text-sm py-2">Drivers</TabsTrigger>
            </TabsList>
            
            {/* Secondary tabs for mobile only */}
            <div className="grid grid-cols-2 gap-2 md:hidden">
              <Button
                variant={activeTab === 'vehicles' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveTab('vehicles')}
                className="text-xs py-2 h-9"
              >
                Vehicles
              </Button>
              <Button
                variant={activeTab === 'drivers' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveTab('drivers')}
                className="text-xs py-2 h-9"
              >
                Drivers
              </Button>
            </div>
          </div>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Orders */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-primary" />
                    Recent Orders
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {orders.slice(0, 5).map((order) => (
                      <div key={order.id} className="flex items-center justify-between p-3 bg-background/50 rounded-lg border border-border/50">
                        <div className="flex-1">
                          <p className="font-semibold">{order.id}</p>
                          <p className="text-sm text-muted-foreground">{order.customerName}</p>
                          <p className="text-xs text-muted-foreground">{order.quantity} kg</p>
                        </div>
                        <Badge className={getStatusColor(order.status)}>
                          {order.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Fleet Status */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Truck className="w-5 h-5 text-primary" />
                    Fleet Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {vehicles.map((vehicle) => (
                      <div key={vehicle.id} className="flex items-center justify-between p-3 bg-background/50 rounded-lg border border-border/50">
                        <div className="flex-1">
                          <p className="font-semibold">{vehicle.number}</p>
                          <p className="text-sm text-muted-foreground">
                            Load: {vehicle.currentLoad}/{vehicle.capacity} kg
                          </p>
                          <p className="text-xs text-muted-foreground">Fuel: {vehicle.fuelLevel}%</p>
                        </div>
                        <Badge className={getStatusColor(vehicle.status)}>
                          {vehicle.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Performance Charts Placeholder */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  Performance Analytics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gradient-to-br from-primary/5 to-accent/5 rounded-lg flex items-center justify-center border border-border/30">
                  <div className="text-center text-muted-foreground">
                    <BarChart3 className="w-16 h-16 mx-auto mb-4 text-primary/50" />
                    <p>Analytics Dashboard</p>
                    <p className="text-sm">(Charts integration: Recharts)</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Order Management</h2>
              <Button className="bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary">
                <Plus className="w-4 h-4 mr-2" />
                New Order
              </Button>
            </div>

            <Card className="border-border/50">
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Order ID</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Address</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Scheduled</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orders.map((order) => (
                      <TableRow key={order.id}>
                        <TableCell className="font-medium">{order.id}</TableCell>
                        <TableCell>{order.customerName}</TableCell>
                        <TableCell className="max-w-xs truncate">{order.deliveryAddress}</TableCell>
                        <TableCell>{order.quantity} kg</TableCell>
                        <TableCell>{new Date(order.scheduledTime).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(order.status)}>
                            {order.status.replace('_', ' ')}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            {order.status === 'PENDING' && (
                              <Dialog open={isAssignDialogOpen} onOpenChange={setIsAssignDialogOpen}>
                                <DialogTrigger asChild>
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    onClick={() => setSelectedOrder(order)}
                                  >
                                    <UserCheck className="w-4 h-4" />
                                  </Button>
                                </DialogTrigger>
                                <DialogContent>
                                  <DialogHeader>
                                    <DialogTitle>Assign Order {selectedOrder?.id}</DialogTitle>
                                  </DialogHeader>
                                  <form onSubmit={handleAssignOrder} className="space-y-4">
                                    <div className="space-y-2">
                                      <Label>Select Driver</Label>
                                      <Select>
                                        <SelectTrigger>
                                          <SelectValue placeholder="Choose driver" />
                                        </SelectTrigger>
                                        <SelectContent>
                                          {drivers.filter(d => d.status === 'ONLINE').map((driver) => (
                                            <SelectItem key={driver.id} value={driver.id}>
                                              {driver.name} - Rating: {driver.rating}
                                            </SelectItem>
                                          ))}
                                        </SelectContent>
                                      </Select>
                                    </div>
                                    <div className="space-y-2">
                                      <Label>Select Vehicle</Label>
                                      <Select>
                                        <SelectTrigger>
                                          <SelectValue placeholder="Choose vehicle" />
                                        </SelectTrigger>
                                        <SelectContent>
                                          {vehicles.filter(v => v.status === 'AVAILABLE').map((vehicle) => (
                                            <SelectItem key={vehicle.id} value={vehicle.id}>
                                              {vehicle.number} - Capacity: {vehicle.capacity} kg
                                            </SelectItem>
                                          ))}
                                        </SelectContent>
                                      </Select>
                                    </div>
                                    <div className="flex gap-4">
                                      <Button type="submit" className="flex-1">Assign</Button>
                                      <Button type="button" variant="outline" onClick={() => setIsAssignDialogOpen(false)}>
                                        Cancel
                                      </Button>
                                    </div>
                                  </form>
                                </DialogContent>
                              </Dialog>
                            )}
                            <Button size="sm" variant="outline">
                              <Edit className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Vehicles Tab */}
          <TabsContent value="vehicles" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Vehicle Management</h2>
              <Dialog open={isVehicleDialogOpen} onOpenChange={setIsVehicleDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Vehicle
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleCreateVehicle} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="vehicleNumber">Vehicle Number</Label>
                      <Input
                        id="vehicleNumber"
                        placeholder="LPG-004"
                        value={newVehicle.number}
                        onChange={(e) => setNewVehicle({...newVehicle, number: e.target.value})}
                        required
                        className="bg-input-background border-border/50"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="capacity">Capacity (kg)</Label>
                      <Input
                        id="capacity"
                        type="number"
                        placeholder="500"
                        value={newVehicle.capacity}
                        onChange={(e) => setNewVehicle({...newVehicle, capacity: e.target.value})}
                        required
                        className="bg-input-background border-border/50"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="status">Status</Label>
                      <Select 
                        value={newVehicle.status}
                        onValueChange={(value: VehicleStatus) => setNewVehicle({...newVehicle, status: value})}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="AVAILABLE">Available</SelectItem>
                          <SelectItem value="MAINTENANCE">Maintenance</SelectItem>
                          <SelectItem value="OUT_OF_SERVICE">Out of Service</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex gap-4">
                      <Button type="submit" className="flex-1">
                        {editingVehicle ? 'Update Vehicle' : 'Add Vehicle'}
                      </Button>
                      <Button type="button" variant="outline" onClick={() => setIsVehicleDialogOpen(false)}>
                        Cancel
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <Card className="border-border/50">
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Vehicle ID</TableHead>
                      <TableHead>Number</TableHead>
                      <TableHead>Capacity</TableHead>
                      <TableHead>Current Load</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Fuel Level</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {vehicles.map((vehicle) => (
                      <TableRow key={vehicle.id}>
                        <TableCell className="font-medium">{vehicle.id}</TableCell>
                        <TableCell>{vehicle.number}</TableCell>
                        <TableCell>{vehicle.capacity} kg</TableCell>
                        <TableCell>{vehicle.currentLoad} kg</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(vehicle.status)}>
                            {vehicle.status.replace('_', ' ')}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${vehicle.fuelLevel > 50 ? 'bg-green-400' : vehicle.fuelLevel > 25 ? 'bg-yellow-400' : 'bg-red-400'}`}></div>
                            {vehicle.fuelLevel}%
                          </div>
                        </TableCell>
                        <TableCell>{vehicle.location}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button size="sm" variant="outline" className="text-red-400 hover:bg-red-500/10">
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Drivers Tab */}
          <TabsContent value="drivers" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Driver Management</h2>
              <Button className="bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary">
                <Plus className="w-4 h-4 mr-2" />
                Add Driver
              </Button>
            </div>

            <Card className="border-border/50">
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Driver ID</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Phone</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Vehicle</TableHead>
                      <TableHead>Rating</TableHead>
                      <TableHead>Deliveries</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {drivers.map((driver) => (
                      <TableRow key={driver.id}>
                        <TableCell className="font-medium">{driver.id}</TableCell>
                        <TableCell>{driver.name}</TableCell>
                        <TableCell>{driver.phone}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(driver.status)}>
                            {driver.status.replace('_', ' ')}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {driver.assignedVehicleId ? 
                            vehicles.find(v => v.id === driver.assignedVehicleId)?.number || 'N/A' 
                            : 'Unassigned'
                          }
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <span>{driver.rating}</span>
                            <span className="text-yellow-400">★</span>
                          </div>
                        </TableCell>
                        <TableCell>{driver.totalDeliveries}</TableCell>
                        <TableCell>{driver.location}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Phone className="w-4 h-4" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <Edit className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Live Tracking Tab */}
          <TabsContent value="tracking" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Live Tracking Monitor</h2>
              <div className="flex gap-2">
                <Button variant="outline" className="border-border/50">
                  <Navigation className="w-4 h-4 mr-2" />
                  Refresh Location
                </Button>
                <Button variant="outline" className="border-border/50">
                  <Settings className="w-4 h-4 mr-2" />
                  Map Settings
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Live Map */}
              <Card className="lg:col-span-2 border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-primary" />
                    Real-Time GPS Tracking
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-96 bg-gradient-to-br from-primary/5 to-accent/5 rounded-lg flex items-center justify-center border border-border/30">
                    <div className="text-center text-muted-foreground">
                      <MapPin className="w-16 h-16 mx-auto mb-4 text-primary/50" />
                      <p className="text-lg font-semibold">Interactive Map View</p>
                      <p className="text-sm">Google Maps / OpenStreetMap Integration</p>
                      <p className="text-xs mt-2">Real-time vehicle positions and delivery routes</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Active Deliveries */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-accent" />
                    Active Deliveries
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {orders.filter(o => ['ASSIGNED', 'ON_ROUTE'].includes(o.status)).map((order) => {
                      const driver = drivers.find(d => d.id === order.assignedDriverId);
                      const vehicle = vehicles.find(v => v.id === order.assignedVehicleId);
                      return (
                        <div key={order.id} className="p-4 bg-background/50 rounded-lg border border-border/50">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold">{order.id}</h4>
                            <Badge className={getStatusColor(order.status)}>
                              {order.status.replace('_', ' ')}
                            </Badge>
                          </div>
                          <div className="space-y-1 text-sm text-muted-foreground">
                            <p>Driver: {driver?.name || 'Unassigned'}</p>
                            <p>Vehicle: {vehicle?.number || 'N/A'}</p>
                            <p>Customer: {order.customerName}</p>
                            <p>Quantity: {order.quantity} kg</p>
                          </div>
                          <div className="flex gap-2 mt-3">
                            <Button size="sm" variant="outline" className="text-xs">
                              <Phone className="w-3 h-3 mr-1" />
                              Call
                            </Button>
                            <Button size="sm" variant="outline" className="text-xs">
                              <MapPin className="w-3 h-3 mr-1" />
                              Track
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Fleet Status Summary */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Truck className="w-5 h-5 text-primary" />
                  Fleet Status Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-primary">{vehicles.filter(v => v.status === 'ASSIGNED').length}</p>
                    <p className="text-sm text-muted-foreground">Vehicles on Route</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-accent">{vehicles.filter(v => v.status === 'AVAILABLE').length}</p>
                    <p className="text-sm text-muted-foreground">Available Vehicles</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-yellow-400">{vehicles.filter(v => v.status === 'MAINTENANCE').length}</p>
                    <p className="text-sm text-muted-foreground">In Maintenance</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}