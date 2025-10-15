import React, { useState } from 'react';
import ChatBox from './ui/chatbox';
import LiveMap from './ui/livemap';
import VoiceAssistant from './ui/voiceassistant';
import { fetchDriverLocation, fetchOrders } from '@/lib/api';
import { getDistance } from 'geolib';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Flame, Plus, MapPin, Clock, Truck, Package, LogOut, Phone } from 'lucide-react';

interface User {
  id: string;
  email: string;
  role: string;
  name: string;
  token: string;
}

interface CustomerDashboardProps {
  user: User;
  onLogout: () => void;
}

type OrderStatus = 'PENDING' | 'ASSIGNED' | 'ON_ROUTE' | 'DELIVERED' | 'CANCELLED';

interface Order {
  id: string;
  deliveryAddress: string;
  pickupLocation: string;
  quantity: number;
  scheduledTime: string;
  contactDetails: string;
  specialInstructions: string;
  status: OrderStatus;
  createdAt: string;
  driverName?: string;
  vehicleNumber?: string;
  estimatedArrival?: string;
}

export function CustomerDashboard({ user, onLogout }: CustomerDashboardProps) {
  const [isOrderDialogOpen, setIsOrderDialogOpen] = useState(false);
  const [orders, setOrders] = useState<Order[]>([
    {
      id: 'ORD-001',
      deliveryAddress: '123 Main St, Downtown City',
      pickupLocation: 'Central Gas Station',
      quantity: 14.2,
      scheduledTime: '2024-01-15T10:00',
      contactDetails: '+1 234-567-8900',
      specialInstructions: 'Please call upon arrival',
      status: 'ON_ROUTE',
      createdAt: '2024-01-14T08:30',
      driverName: 'John Smith',
      vehicleNumber: 'LPG-001',
      estimatedArrival: '10:30 AM'
    },
    {
      id: 'ORD-002',
      deliveryAddress: '456 Oak Avenue, Suburb Area',
      pickupLocation: 'East Side Depot',
      quantity: 9.5,
      scheduledTime: '2024-01-14T14:00',
      contactDetails: '+1 234-567-8901',
      specialInstructions: 'Gate code: 1234',
      status: 'DELIVERED',
      createdAt: '2024-01-13T12:15',
      driverName: 'Mike Johnson',
      vehicleNumber: 'LPG-003'
    }
  ]);

  const [newOrder, setNewOrder] = useState({
    deliveryAddress: '',
    pickupLocation: '',
    quantity: '',
    scheduledTime: '',
    contactDetails: '',
    specialInstructions: ''
  });

  const handleCreateOrder = (e: React.FormEvent) => {
    e.preventDefault();
    
    const order: Order = {
      id: `ORD-${String(orders.length + 1).padStart(3, '0')}`,
      deliveryAddress: newOrder.deliveryAddress,
      pickupLocation: newOrder.pickupLocation,
      quantity: parseFloat(newOrder.quantity),
      scheduledTime: newOrder.scheduledTime,
      contactDetails: newOrder.contactDetails,
      specialInstructions: newOrder.specialInstructions,
      status: 'PENDING',
      createdAt: new Date().toISOString()
    };

    setOrders([order, ...orders]);
    setNewOrder({
      deliveryAddress: '',
      pickupLocation: '',
      quantity: '',
      scheduledTime: '',
      contactDetails: '',
      specialInstructions: ''
    });
    setIsOrderDialogOpen(false);
  };

  const getStatusColor = (status: OrderStatus) => {
    switch (status) {
      case 'PENDING': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'ASSIGNED': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'ON_ROUTE': return 'bg-primary/20 text-primary border-primary/30';
      case 'DELIVERED': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'CANCELLED': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-muted';
    }
  };

  const activeOrders = orders.filter(order => ['PENDING', 'ASSIGNED', 'ON_ROUTE'].includes(order.status));
  const completedOrders = orders.filter(order => ['DELIVERED', 'CANCELLED'].includes(order.status));

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 md:gap-3">
              <div className="relative">
                <Flame className="w-6 h-6 md:w-8 md:h-8 text-primary" />
                <div className="absolute inset-0 w-6 h-6 md:w-8 md:h-8 bg-primary/20 rounded-full blur-lg"></div>
              </div>
              <div>
                <h1 className="text-lg md:text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Ugunja Customer
                </h1>
                <p className="text-xs md:text-sm text-muted-foreground">Welcome back, {user.name}</p>
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
                  <p className="text-lg md:text-2xl font-bold">{orders.length}</p>
                </div>
                <Package className="w-6 h-6 md:w-8 md:h-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-accent/5">
            <CardContent className="p-3 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">Active Orders</p>
                  <p className="text-lg md:text-2xl font-bold">{activeOrders.length}</p>
                </div>
                <Truck className="w-6 h-6 md:w-8 md:h-8 text-accent" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-primary/5">
            <CardContent className="p-3 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">Completed</p>
                  <p className="text-lg md:text-2xl font-bold">{completedOrders.length}</p>
                </div>
                <Clock className="w-6 h-6 md:w-8 md:h-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-accent/5">
            <CardContent className="p-3 md:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">Total LPG (kg)</p>
                  <p className="text-lg md:text-2xl font-bold">
                    {orders.reduce((sum, order) => sum + order.quantity, 0).toFixed(1)}
                  </p>
                </div>
                <Flame className="w-6 h-6 md:w-8 md:h-8 text-accent" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Orders Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">My Orders</h2>
              <Dialog open={isOrderDialogOpen} onOpenChange={setIsOrderDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary">
                    <Plus className="w-4 h-4 mr-2" />
                    New Order
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Create New LPG Order</DialogTitle>
                    <DialogDescription>
                      Fill in the details below to place a new LPG delivery order. All required fields must be completed.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreateOrder} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="deliveryAddress">Delivery Address *</Label>
                        <Textarea
                          id="deliveryAddress"
                          placeholder="Enter complete delivery address"
                          value={newOrder.deliveryAddress}
                          onChange={(e) => setNewOrder({...newOrder, deliveryAddress: e.target.value})}
                          required
                          className="bg-input-background border-border/50"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="pickupLocation">Pickup Location *</Label>
                        <Input
                          id="pickupLocation"
                          placeholder="e.g., Central Gas Station"
                          value={newOrder.pickupLocation}
                          onChange={(e) => setNewOrder({...newOrder, pickupLocation: e.target.value})}
                          required
                          className="bg-input-background border-border/50"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="quantity">Quantity (kg) *</Label>
                        <Input
                          id="quantity"
                          type="number"
                          step="0.1"
                          min="1"
                          placeholder="14.2"
                          value={newOrder.quantity}
                          onChange={(e) => setNewOrder({...newOrder, quantity: e.target.value})}
                          required
                          className="bg-input-background border-border/50"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="scheduledTime">Scheduled Time *</Label>
                        <Input
                          id="scheduledTime"
                          type="datetime-local"
                          value={newOrder.scheduledTime}
                          onChange={(e) => setNewOrder({...newOrder, scheduledTime: e.target.value})}
                          required
                          className="bg-input-background border-border/50"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="contactDetails">Contact Details *</Label>
                      <Input
                        id="contactDetails"
                        placeholder="Phone number or email"
                        value={newOrder.contactDetails}
                        onChange={(e) => setNewOrder({...newOrder, contactDetails: e.target.value})}
                        required
                        className="bg-input-background border-border/50"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="specialInstructions">Special Instructions</Label>
                      <Textarea
                        id="specialInstructions"
                        placeholder="Any special delivery instructions..."
                        value={newOrder.specialInstructions}
                        onChange={(e) => setNewOrder({...newOrder, specialInstructions: e.target.value})}
                        className="bg-input-background border-border/50"
                      />
                    </div>

                    <div className="flex gap-4 pt-4">
                      <Button type="submit" className="flex-1 bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary">
                        Create Order
                      </Button>
                      <Button type="button" variant="outline" onClick={() => setIsOrderDialogOpen(false)}>
                        Cancel
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <Tabs defaultValue="active" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="active">Active Orders ({activeOrders.length})</TabsTrigger>
                <TabsTrigger value="history">Order History ({completedOrders.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="active" className="space-y-4">
                {activeOrders.length === 0 ? (
                  <Card className="border-border/50">
                    <CardContent className="p-8 text-center">
                      <Package className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">No active orders. Create your first order!</p>
                    </CardContent>
                  </Card>
                ) : (
                  activeOrders.map((order) => (
                    <Card key={order.id} className="border-border/50 bg-gradient-to-r from-card to-card/50">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="font-bold text-lg">Order {order.id}</h3>
                            <p className="text-sm text-muted-foreground">
                              Created: {new Date(order.createdAt).toLocaleDateString()}
                            </p>
                          </div>
                          <Badge className={getStatusColor(order.status)}>
                            {order.status.replace('_', ' ')}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <MapPin className="w-4 h-4 text-primary" />
                              <span className="text-sm">From: {order.pickupLocation}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <MapPin className="w-4 h-4 text-accent" />
                              <span className="text-sm">To: {order.deliveryAddress}</span>
                            </div>
                          </div>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Flame className="w-4 h-4 text-primary" />
                              <span className="text-sm">Quantity: {order.quantity} kg</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-accent" />
                              <span className="text-sm">
                                Scheduled: {new Date(order.scheduledTime).toLocaleString()}
                              </span>
                            </div>
                          </div>
                        </div>

                        {order.status === 'ON_ROUTE' && order.driverName && (
                          <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                            <h4 className="font-semibold mb-2">Delivery in Progress</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                              <div>Driver: {order.driverName}</div>
                              <div>Vehicle: {order.vehicleNumber}</div>
                              {order.estimatedArrival && (
                                <div>ETA: {order.estimatedArrival}</div>
                              )}
                              <div className="flex items-center gap-2">
                                <Phone className="w-4 h-4" />
                                {order.contactDetails}
                              </div>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))
                )}
              </TabsContent>

              <TabsContent value="history" className="space-y-4">
                {completedOrders.map((order) => (
                  <Card key={order.id} className="border-border/50">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-bold">Order {order.id}</h3>
                          <p className="text-sm text-muted-foreground">
                            {new Date(order.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge className={getStatusColor(order.status)}>
                          {order.status}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        <p>{order.deliveryAddress} • {order.quantity} kg</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>
            </Tabs>
          </div>

          {/* Live Tracking Panel */}
          <div className="lg:col-span-1">
            <Card className="border-border/50 bg-gradient-to-br from-card to-primary/5 h-fit">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-primary" />
                  Live Tracking
                </CardTitle>
              </CardHeader>
              <CardContent>
                {activeOrders.filter(order => order.status === 'ON_ROUTE').length > 0 ? (
                  <div className="space-y-4">
                    {activeOrders.filter(order => order.status === 'ON_ROUTE').map((order) => (
                      <div key={order.id} className="p-4 bg-background/50 rounded-lg border border-border/50">
                        <h4 className="font-semibold mb-2">Order {order.id}</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Driver:</span>
                            <span>{order.driverName}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Vehicle:</span>
                            <span>{order.vehicleNumber}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>ETA:</span>
                            <span className="text-primary">{order.estimatedArrival}</span>
                          </div>
                        </div>
                        <div className="mt-4 h-32 bg-muted/20 rounded-lg flex items-center justify-center border border-border/30">
                          <div className="text-center text-muted-foreground">
                            <MapPin className="w-8 h-8 mx-auto mb-2" />
                            <p className="text-sm">Interactive Map</p>
                            <p className="text-xs">(Google Maps Integration)</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <MapPin className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No active deliveries to track</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}