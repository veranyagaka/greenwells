import React, { useState } from 'react';
import ChatBox from './ui/chatbox';
import LiveMap from './ui/livemap';
import VoiceAssistant from './ui/voiceassistant';
import { fetchDriverLocation } from '@/lib/api';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Flame, Navigation, Package, Clock, LogOut, MapPin, Truck, Phone, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface User {
  id: string;
  email: string;
  role: string;
  name: string;
  token: string;
}

interface DriverDashboardProps {
  user: User;
  onLogout: () => void;
}

type DeliveryStatus = 'ASSIGNED' | 'ON_ROUTE' | 'DELIVERED' | 'CANCELLED';

interface Delivery {
  id: string;
  orderId: string;
  customerName: string;
  customerPhone: string;
  deliveryAddress: string;
  pickupLocation: string;
  quantity: number;
  scheduledTime: string;
  specialInstructions: string;
  status: DeliveryStatus;
  assignedAt: string;
  vehicleNumber: string;
  dispatcherName: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  estimatedDistance: string;
}

export function DriverDashboard({ user, onLogout }: DriverDashboardProps) {
  const [isGpsDialogOpen, setIsGpsDialogOpen] = useState(false);
  const [selectedDelivery, setSelectedDelivery] = useState<Delivery | null>(null);
  const [gpsData, setGpsData] = useState({
    latitude: '',
    longitude: '',
    notes: ''
  });

  const [deliveries, setDeliveries] = useState<Delivery[]>([
    {
      id: 'DEL-001',
      orderId: 'ORD-001',
      customerName: 'Sarah Johnson',
      customerPhone: '+1 234-567-8900',
      deliveryAddress: '123 Main St, Downtown City',
      pickupLocation: 'Central Gas Station',
      quantity: 14.2,
      scheduledTime: '2024-01-15T10:00',
      specialInstructions: 'Please call upon arrival. Gate code: 1234',
      status: 'ASSIGNED',
      assignedAt: '2024-01-14T08:30',
      vehicleNumber: 'LPG-001',
      dispatcherName: 'Mike Rodriguez',
      priority: 'HIGH',
      estimatedDistance: '5.2 km'
    },
    {
      id: 'DEL-002',
      orderId: 'ORD-005',
      customerName: 'Robert Chen',
      customerPhone: '+1 234-567-8901',
      deliveryAddress: '456 Oak Avenue, Suburb Area',
      pickupLocation: 'Central Gas Station',
      quantity: 9.5,
      scheduledTime: '2024-01-15T14:00',
      specialInstructions: 'Side entrance delivery preferred',
      status: 'ON_ROUTE',
      assignedAt: '2024-01-14T12:15',
      vehicleNumber: 'LPG-001',
      dispatcherName: 'Mike Rodriguez',
      priority: 'MEDIUM',
      estimatedDistance: '8.7 km'
    },
    {
      id: 'DEL-003',
      orderId: 'ORD-003',
      customerName: 'Emily Davis',
      customerPhone: '+1 234-567-8902',
      deliveryAddress: '789 Pine Street, East District',
      pickupLocation: 'Central Gas Station',
      quantity: 12.0,
      scheduledTime: '2024-01-14T16:00',
      specialInstructions: 'Delivered successfully',
      status: 'DELIVERED',
      assignedAt: '2024-01-14T10:00',
      vehicleNumber: 'LPG-001',
      dispatcherName: 'Mike Rodriguez',
      priority: 'MEDIUM',
      estimatedDistance: '3.1 km'
    }
  ]);

  const updateDeliveryStatus = (deliveryId: string, newStatus: DeliveryStatus) => {
    setDeliveries((prev) =>
      prev.map((delivery) =>
        delivery.id === deliveryId ? { ...delivery, status: newStatus } : delivery
      )
    );
  };

  const handleGpsSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedDelivery) {
      // In a real app, this would send GPS data to the backend
      console.log('GPS data submitted:', {
        deliveryId: selectedDelivery.id,
        ...gpsData,
        timestamp: new Date().toISOString()
      });
      
      setGpsData({ latitude: '', longitude: '', notes: '' });
      setIsGpsDialogOpen(false);
      setSelectedDelivery(null);
      
      // Show success message (in real app, use toast)
      alert('GPS location updated successfully!');
    }
  };

  const getStatusColor = (status: DeliveryStatus) => {
    switch (status) {
      case 'ASSIGNED': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'ON_ROUTE': return 'bg-primary/20 text-primary border-primary/30';
      case 'DELIVERED': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'CANCELLED': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-muted';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'MEDIUM': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'LOW': return 'bg-green-500/20 text-green-400 border-green-500/30';
      default: return 'bg-muted';
    }
  };

  const activeDeliveries = deliveries.filter(d => ['ASSIGNED', 'ON_ROUTE'].includes(d.status));
  const completedDeliveries = deliveries.filter(d => ['DELIVERED', 'CANCELLED'].includes(d.status));

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 md:gap-3">
              <div className="relative">
                <Truck className="w-6 h-6 md:w-8 md:h-8 text-primary" />
                <div className="absolute inset-0 w-6 h-6 md:w-8 md:h-8 bg-primary/20 rounded-full blur-lg"></div>
              </div>
              <div>
                <h1 className="text-lg md:text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Ugunja Driver
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
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Today's Deliveries</p>
                  <p className="text-2xl font-bold">{activeDeliveries.length}</p>
                </div>
                <Package className="w-8 h-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-accent/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Completed</p>
                  <p className="text-2xl font-bold">{completedDeliveries.filter(d => d.status === 'DELIVERED').length}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-accent" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-primary/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Vehicle</p>
                  <p className="text-2xl font-bold">LPG-001</p>
                </div>
                <Truck className="w-8 h-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-gradient-to-br from-card to-accent/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Distance</p>
                  <p className="text-2xl font-bold">17.0 km</p>
                </div>
                <Navigation className="w-8 h-8 text-accent" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Deliveries Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">My Deliveries</h2>
              <Dialog open={isGpsDialogOpen} onOpenChange={setIsGpsDialogOpen}>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    className="border-primary/50 hover:bg-primary/10"
                    onClick={() => {
                      // Auto-fill current location if available
                      if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition((position) => {
                          setGpsData({
                            latitude: position.coords.latitude.toString(),
                            longitude: position.coords.longitude.toString(),
                            notes: ''
                          });
                        });
                      }
                    }}
                  >
                    <Navigation className="w-4 h-4 mr-2" />
                    Submit GPS Log
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Submit GPS Location</DialogTitle>
                    <DialogDescription>
                      Submit your current GPS coordinates to update your location in the tracking system.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleGpsSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="latitude">Latitude *</Label>
                        <Input
                          id="latitude"
                          placeholder="40.7128"
                          value={gpsData.latitude}
                          onChange={(e) => setGpsData({...gpsData, latitude: e.target.value})}
                          required
                          className="bg-input-background border-border/50"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="longitude">Longitude *</Label>
                        <Input
                          id="longitude"
                          placeholder="-74.0060"
                          value={gpsData.longitude}
                          onChange={(e) => setGpsData({...gpsData, longitude: e.target.value})}
                          required
                          className="bg-input-background border-border/50"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="notes">Notes (Optional)</Label>
                      <Textarea
                        id="notes"
                        placeholder="Additional location notes..."
                        value={gpsData.notes}
                        onChange={(e) => setGpsData({...gpsData, notes: e.target.value})}
                        className="bg-input-background border-border/50"
                      />
                    </div>
                    <div className="flex gap-4">
                      <Button type="submit" className="flex-1 bg-gradient-to-r from-primary to-accent">
                        Submit Location
                      </Button>
                      <Button type="button" variant="outline" onClick={() => setIsGpsDialogOpen(false)}>
                        Cancel
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <Tabs defaultValue="active" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="active">Active Deliveries ({activeDeliveries.length})</TabsTrigger>
                <TabsTrigger value="completed">Completed ({completedDeliveries.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="active" className="space-y-4">
                {activeDeliveries.length === 0 ? (
                  <Card className="border-border/50">
                    <CardContent className="p-8 text-center">
                      <Package className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">No active deliveries assigned</p>
                    </CardContent>
                  </Card>
                ) : (
                  activeDeliveries.map((delivery) => (
                    <Card key={delivery.id} className="border-border/50 bg-gradient-to-r from-card to-card/50">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="font-bold text-lg">Order {delivery.orderId}</h3>
                            <p className="text-sm text-muted-foreground">
                              Assigned: {new Date(delivery.assignedAt).toLocaleString()}
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <Badge className={getPriorityColor(delivery.priority)}>
                              {delivery.priority}
                            </Badge>
                            <Badge className={getStatusColor(delivery.status)}>
                              {delivery.status.replace('_', ' ')}
                            </Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Package className="w-4 h-4 text-primary" />
                              <span className="text-sm">Customer: {delivery.customerName}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Phone className="w-4 h-4 text-accent" />
                              <span className="text-sm">{delivery.customerPhone}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Flame className="w-4 h-4 text-primary" />
                              <span className="text-sm">Quantity: {delivery.quantity} kg</span>
                            </div>
                          </div>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <MapPin className="w-4 h-4 text-primary" />
                              <span className="text-sm">From: {delivery.pickupLocation}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <MapPin className="w-4 h-4 text-accent" />
                              <span className="text-sm">To: {delivery.deliveryAddress}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Navigation className="w-4 h-4 text-primary" />
                              <span className="text-sm">Distance: {delivery.estimatedDistance}</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 mb-4">
                          <Clock className="w-4 h-4 text-accent" />
                          <span className="text-sm">
                            Scheduled: {new Date(delivery.scheduledTime).toLocaleString()}
                          </span>
                        </div>

                        {delivery.specialInstructions && (
                          <div className="bg-accent/10 border border-accent/20 rounded-lg p-3 mb-4">
                            <div className="flex items-start gap-2">
                              <AlertCircle className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                              <div>
                                <h4 className="text-sm font-semibold">Special Instructions:</h4>
                                <p className="text-sm text-muted-foreground">{delivery.specialInstructions}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        <div className="flex flex-wrap gap-2">
                          {delivery.status === 'ASSIGNED' && (
                            <Button 
                              onClick={() => updateDeliveryStatus(delivery.id, 'ON_ROUTE')}
                              className="bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary"
                            >
                              Start Delivery
                            </Button>
                          )}
                          {delivery.status === 'ON_ROUTE' && (
                            <>
                              <Button 
                                onClick={() => updateDeliveryStatus(delivery.id, 'DELIVERED')}
                                className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-600"
                              >
                                <CheckCircle className="w-4 h-4 mr-2" />
                                Mark Delivered
                              </Button>
                              <Button 
                                variant="outline"
                                onClick={() => updateDeliveryStatus(delivery.id, 'CANCELLED')}
                                className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                              >
                                <XCircle className="w-4 h-4 mr-2" />
                                Cancel
                              </Button>
                            </>
                          )}
                          <Button 
                            variant="outline"
                            onClick={() => {
                              setSelectedDelivery(delivery);
                              setIsGpsDialogOpen(true);
                            }}
                            className="border-border/50"
                          >
                            <Navigation className="w-4 h-4 mr-2" />
                            Update GPS
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </TabsContent>

              <TabsContent value="completed" className="space-y-4">
                {completedDeliveries.map((delivery) => (
                  <Card key={delivery.id} className="border-border/50">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-bold">Order {delivery.orderId}</h3>
                          <p className="text-sm text-muted-foreground">
                            {delivery.customerName} • {delivery.quantity} kg
                          </p>
                        </div>
                        <Badge className={getStatusColor(delivery.status)}>
                          {delivery.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{delivery.deliveryAddress}</p>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>
            </Tabs>
          </div>

          {/* Vehicle Info & Dispatcher Contact */}
          <div className="lg:col-span-1 space-y-6">
            {/* Vehicle Information */}
            <Card className="border-border/50 bg-gradient-to-br from-card to-primary/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Truck className="w-5 h-5 text-primary" />
                  Vehicle Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Vehicle Number:</span>
                  <span className="text-sm font-semibold">LPG-001</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Capacity:</span>
                  <span className="text-sm font-semibold">500 kg</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Current Load:</span>
                  <span className="text-sm font-semibold">23.7 kg</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Fuel Level:</span>
                  <span className="text-sm font-semibold text-green-400">85%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Last Service:</span>
                  <span className="text-sm font-semibold">Dec 15, 2023</span>
                </div>
              </CardContent>
            </Card>

            {/* Dispatcher Contact */}
            <Card className="border-border/50 bg-gradient-to-br from-card to-accent/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="w-5 h-5 text-accent" />
                  Dispatcher Contact
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Name:</span>
                  <span className="text-sm font-semibold">Mike Rodriguez</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Phone:</span>
                  <span className="text-sm font-semibold">+1 234-567-9000</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Radio:</span>
                  <span className="text-sm font-semibold">Channel 7</span>
                </div>
                <Button variant="outline" className="w-full mt-4 border-accent/50 hover:bg-accent/10">
                  <Phone className="w-4 h-4 mr-2" />
                  Call Dispatcher
                </Button>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full border-border/50">
                  <MapPin className="w-4 h-4 mr-2" />
                  Open Navigation
                </Button>
                <Button variant="outline" className="w-full border-border/50">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Report Issue
                </Button>
                <Button variant="outline" className="w-full border-border/50">
                  <Clock className="w-4 h-4 mr-2" />
                  Break Time
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}