from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Vehicle, DriverAssignment, Order, Delivery, TrackingLog

User = get_user_model()


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model."""
    
    class Meta:
        model = Vehicle
        fields = ['id', 'plate_number', 'model', 'capacity_kg', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for DriverAssignment model."""
    
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate_number', read_only=True)
    
    class Meta:
        model = DriverAssignment
        fields = ['id', 'driver', 'driver_name', 'vehicle', 'vehicle_plate', 
                 'start_date', 'end_date']
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate driver assignment dates."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""
    
    class Meta:
        model = Order
        fields = ['delivery_address', 'quantity_kg', 'scheduled_time', 
                 'pickup_address', 'customer_phone', 'special_instructions']
    
    def validate_quantity_kg(self, value):
        """Validate LPG quantity."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        if value > 1000:  # Maximum reasonable quantity
            raise serializers.ValidationError("Quantity cannot exceed 1000 kg.")
        return value
    
    def validate_scheduled_time(self, value):
        """Validate scheduled delivery time."""
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        
        # Don't allow scheduling more than 30 days in advance
        max_future = timezone.now() + timedelta(days=30)
        if value > max_future:
            raise serializers.ValidationError("Cannot schedule more than 30 days in advance.")
        
        return value
    
    def create(self, validated_data):
        """Create order with authenticated customer."""
        customer = self.context['request'].user
        if customer.role != 'CUSTOMER':
            raise serializers.ValidationError("Only customers can create orders.")
        
        validated_data['customer'] = customer
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for viewing orders."""
    
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'customer_email',
                 'delivery_address', 'pickup_address', 'quantity_kg', 'status', 
                 'scheduled_time', 'customer_phone', 'special_instructions',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status."""
    
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transitions."""
        instance = self.instance
        if not instance:
            return value
            
        current_status = instance.status
        valid_transitions = {
            'PENDING': ['ASSIGNED', 'CANCELLED'],
            'ASSIGNED': ['ON_ROUTE', 'CANCELLED'],
            'ON_ROUTE': ['DELIVERED', 'CANCELLED'],
            'DELIVERED': [],  # Final state
            'CANCELLED': []   # Final state
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}."
            )
        
        return value


class DeliverySerializer(serializers.ModelSerializer):
    """Serializer for Delivery model."""
    
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate_number', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    
    class Meta:
        model = Delivery
        fields = ['id', 'order_id', 'driver', 'driver_name', 'vehicle', 
                 'vehicle_plate', 'assigned_by', 'assigned_by_name',
                 'assigned_at', 'started_at', 'completed_at', 'status',
                 'delivery_notes', 'failure_reason']
        read_only_fields = ['id', 'assigned_at', 'assigned_by']


class DeliveryAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning delivery to driver."""
    
    order_id = serializers.IntegerField()
    driver_id = serializers.IntegerField(required=False)
    vehicle_id = serializers.IntegerField(required=False)
    
    def validate_order_id(self, value):
        """Validate order exists and is pending."""
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        if order.status != 'PENDING':
            raise serializers.ValidationError("Only pending orders can be assigned.")
        
        # Check if order already has a delivery
        if hasattr(order, 'delivery'):
            raise serializers.ValidationError("Order already has an assigned delivery.")
        
        return value
    
    def validate_driver_id(self, value):
        """Validate driver exists and is available."""
        if value:
            try:
                driver = User.objects.get(id=value, role='DRIVER', is_active=True)
            except User.DoesNotExist:
                raise serializers.ValidationError("Driver not found or inactive.")
        return value
    
    def validate_vehicle_id(self, value):
        """Validate vehicle exists and is available."""
        if value:
            try:
                vehicle = Vehicle.objects.get(id=value, status='ACTIVE')
            except Vehicle.DoesNotExist:
                raise serializers.ValidationError("Vehicle not found or not active.")
        return value


class TrackingLogSerializer(serializers.ModelSerializer):
    """Serializer for TrackingLog model."""
    
    class Meta:
        model = TrackingLog
        fields = ['id', 'delivery', 'latitude', 'longitude', 'timestamp',
                 'speed', 'heading', 'accuracy']
        read_only_fields = ['id', 'timestamp']
    
    def validate_latitude(self, value):
        """Validate latitude range."""
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude range."""
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value