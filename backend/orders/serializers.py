from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from .models import (
    Vehicle, DriverAssignment, Order, Delivery, TrackingLog,
    Cylinder, CylinderHistory, CylinderScan
)

User = get_user_model()


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model."""
    
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    driver_email = serializers.CharField(source='driver.email', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'plate_number', 'model', 'capacity_kg', 'status', 
                 'driver', 'driver_name', 'driver_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vehicles."""
    
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'model', 'capacity_kg', 'status']
    
    def validate_capacity_kg(self, value):
        """Validate vehicle capacity."""
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0.")
        if value > 5000:  # Maximum reasonable capacity
            raise serializers.ValidationError("Capacity cannot exceed 5000 kg.")
        return value
    
    def validate_plate_number(self, value):
        """Validate plate number format."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Plate number is too short.")
        return value.strip().upper()


class VehicleDriverAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning/unassigning driver to vehicle."""
    
    vehicle_id = serializers.IntegerField()
    driver_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_vehicle_id(self, value):
        """Validate vehicle exists."""
        try:
            vehicle = Vehicle.objects.get(id=value)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError("Vehicle not found.")
        
        if vehicle.status != 'ACTIVE':
            raise serializers.ValidationError("Can only assign drivers to active vehicles.")
        
        return value
    
    def validate_driver_id(self, value):
        """Validate driver exists and is available."""
        if value is not None:
            try:
                driver = User.objects.get(id=value, role='DRIVER', is_active=True)
            except User.DoesNotExist:
                raise serializers.ValidationError("Driver not found or inactive.")
            
            # Check if driver is already assigned to another vehicle
            try:
                current_vehicle = Vehicle.objects.get(driver=driver)
                raise serializers.ValidationError(
                    f"Driver is already assigned to vehicle {current_vehicle.plate_number}."
                )
            except Vehicle.DoesNotExist:
                # Driver is not assigned to any vehicle, which is good
                pass
        
        return value


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


# ============= CYLINDER MANAGEMENT SERIALIZERS =============

class CylinderSerializer(serializers.ModelSerializer):
    """Serializer for Cylinder model with security-conscious fields."""
    
    customer_name = serializers.CharField(source='current_customer.username', read_only=True)
    customer_email = serializers.CharField(source='current_customer.email', read_only=True)
    order_id = serializers.IntegerField(source='current_order.id', read_only=True)
    is_expired = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Cylinder
        fields = [
            'id', 'serial_number', 'qr_code', 'rfid_tag',
            'cylinder_type', 'capacity_kg', 'manufacturer',
            'manufacturing_date', 'expiry_date', 'status',
            'current_customer', 'customer_name', 'customer_email',
            'current_order', 'order_id', 'last_known_location',
            'last_scanned_at', 'last_inspection_date', 'next_inspection_date',
            'total_fills', 'total_scans', 'is_authentic', 'is_tampered',
            'tamper_notes', 'is_expired', 'verification_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'qr_code', 'rfid_tag', 'total_fills', 'total_scans',
            'last_scanned_at', 'created_at', 'updated_at'
        ]
        # Hide sensitive security fields
        extra_kwargs = {
            'secret_key': {'write_only': True},
            'auth_hash': {'write_only': True},
        }
    
    def get_is_expired(self, obj):
        """Check if cylinder has expired."""
        return obj.expiry_date < timezone.now().date()
    
    def get_verification_status(self, obj):
        """Get current verification status."""
        if obj.is_tampered:
            return "TAMPERED"
        if not obj.is_authentic:
            return "NON_AUTHENTIC"
        if obj.expiry_date < timezone.now().date():
            return "EXPIRED"
        if obj.status == 'STOLEN':
            return "STOLEN"
        return "VERIFIED"


class CylinderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new cylinders."""
    
    class Meta:
        model = Cylinder
        fields = [
            'serial_number', 'cylinder_type', 'capacity_kg',
            'manufacturer', 'manufacturing_date', 'expiry_date'
        ]
    
    def validate_serial_number(self, value):
        """Validate serial number format and uniqueness."""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Serial number too short. Minimum 5 characters.")
        
        # Check for valid format (alphanumeric with hyphens)
        if not value.replace('-', '').isalnum():
            raise serializers.ValidationError("Serial number can only contain letters, numbers, and hyphens.")
        
        return value.strip().upper()
    
    def validate_capacity_kg(self, value):
        """Validate capacity matches cylinder type."""
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0.")
        if value > 100:
            raise serializers.ValidationError("Capacity cannot exceed 100 kg.")
        return value
    
    def validate_manufacturing_date(self, value):
        """Validate manufacturing date."""
        if value > timezone.now().date():
            raise serializers.ValidationError("Manufacturing date cannot be in the future.")
        
        # Cylinders older than 20 years should not be registered
        twenty_years_ago = timezone.now().date().replace(year=timezone.now().year - 20)
        if value < twenty_years_ago:
            raise serializers.ValidationError("Cylinder too old. Manufacturing date must be within last 20 years.")
        
        return value
    
    def validate_expiry_date(self, value):
        """Validate expiry date."""
        if value <= timezone.now().date():
            raise serializers.ValidationError("Expiry date must be in the future.")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        manufacturing_date = data.get('manufacturing_date')
        expiry_date = data.get('expiry_date')
        
        if manufacturing_date and expiry_date:
            if expiry_date <= manufacturing_date:
                raise serializers.ValidationError(
                    "Expiry date must be after manufacturing date."
                )
            
            # Typical LPG cylinder lifespan is 15 years
            max_expiry = manufacturing_date.replace(year=manufacturing_date.year + 20)
            if expiry_date > max_expiry:
                raise serializers.ValidationError(
                    "Expiry date too far in future. Maximum lifespan is 20 years."
                )
        
        return data


class CylinderScanSerializer(serializers.Serializer):
    """Serializer for QR/RFID scan operations."""
    
    code = serializers.CharField(required=True, max_length=255)
    scan_type = serializers.ChoiceField(choices=['QR', 'RFID', 'MANUAL'], default='QR')
    location_lat = serializers.FloatField(required=False, allow_null=True)
    location_lng = serializers.FloatField(required=False, allow_null=True)
    location_address = serializers.CharField(required=False, allow_blank=True)
    order_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_code(self, value):
        """Validate scan code format."""
        if len(value.strip()) < 8:
            raise serializers.ValidationError("Invalid code format.")
        return value.strip().upper()
    
    def validate_location_lat(self, value):
        """Validate latitude."""
        if value is not None and not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value
    
    def validate_location_lng(self, value):
        """Validate longitude."""
        if value is not None and not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value


class CylinderHistorySerializer(serializers.ModelSerializer):
    """Serializer for cylinder history records."""
    
    cylinder_serial = serializers.CharField(source='cylinder.serial_number', read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)
    
    class Meta:
        model = CylinderHistory
        fields = [
            'id', 'cylinder', 'cylinder_serial', 'event_type', 'event_date',
            'customer', 'customer_name', 'driver', 'driver_name',
            'order', 'delivery', 'previous_status', 'new_status',
            'location', 'notes', 'performed_by', 'performed_by_name',
            'verification_data'
        ]
        read_only_fields = ['id', 'event_date']


class CylinderScanLogSerializer(serializers.ModelSerializer):
    """Serializer for cylinder scan log records."""
    
    cylinder_serial = serializers.CharField(source='cylinder.serial_number', read_only=True)
    scanned_by_name = serializers.CharField(source='scanned_by.username', read_only=True)
    
    class Meta:
        model = CylinderScan
        fields = [
            'id', 'cylinder', 'cylinder_serial', 'scan_type', 'scan_result',
            'scanned_by', 'scanned_by_name', 'scanner_role',
            'scan_timestamp', 'scan_location_lat', 'scan_location_lng',
            'scan_location_address', 'verification_message',
            'is_suspicious', 'suspicious_reason',
            'related_order', 'related_delivery'
        ]
        read_only_fields = [
            'id', 'scan_timestamp', 'scan_result', 'verification_message',
            'is_suspicious', 'suspicious_reason'
        ]


class CylinderAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning cylinders to orders/customers."""
    
    cylinder_id = serializers.UUIDField()
    order_id = serializers.IntegerField(required=False, allow_null=True)
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_cylinder_id(self, value):
        """Validate cylinder exists and is available."""
        try:
            cylinder = Cylinder.objects.get(id=value)
        except Cylinder.DoesNotExist:
            raise serializers.ValidationError("Cylinder not found.")
        
        if cylinder.status == 'RETIRED':
            raise serializers.ValidationError("Cannot assign retired cylinder.")
        
        if cylinder.status == 'STOLEN':
            raise serializers.ValidationError("Cylinder reported as stolen.")
        
        return value
    
    def validate_order_id(self, value):
        """Validate order exists."""
        if value:
            try:
                order = Order.objects.get(id=value)
                if order.status in ['DELIVERED', 'CANCELLED']:
                    raise serializers.ValidationError("Cannot assign cylinder to completed order.")
            except Order.DoesNotExist:
                raise serializers.ValidationError("Order not found.")
        return value
    
    def validate_customer_id(self, value):
        """Validate customer exists."""
        if value:
            try:
                customer = User.objects.get(id=value, role='CUSTOMER')
            except User.DoesNotExist:
                raise serializers.ValidationError("Customer not found.")
        return value


class CylinderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating cylinder status."""
    
    status = serializers.ChoiceField(choices=Cylinder.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        """Validate status transitions."""
        instance = self.context.get('cylinder')
        if not instance:
            return value
        
        current_status = instance.status
        
        # Define valid transitions
        valid_transitions = {
            'ACTIVE': ['FILLED', 'MAINTENANCE', 'RETIRED', 'STOLEN'],
            'FILLED': ['IN_DELIVERY', 'EMPTY', 'MAINTENANCE'],
            'IN_DELIVERY': ['FILLED', 'EMPTY'],
            'EMPTY': ['FILLED', 'MAINTENANCE', 'RETIRED'],
            'MAINTENANCE': ['ACTIVE', 'RETIRED'],
            'RETIRED': [],  # Final state
            'STOLEN': ['ACTIVE'],  # Can recover stolen cylinders
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}."
            )
        
        return value