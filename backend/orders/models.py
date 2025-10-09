from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
import hashlib
import secrets


class Vehicle(models.Model):
    """Vehicle model for delivery trucks."""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('IN_MAINTENANCE', 'In Maintenance'),
        ('RETIRED', 'Retired'),
    ]
    
    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    capacity_kg = models.FloatField(validators=[MinValueValidator(0.0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'DRIVER'},
        related_name='assigned_vehicle'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
        ordering = ['-created_at']
    
    def __str__(self):
        driver_info = f" - Driver: {self.driver.username}" if self.driver else " - Unassigned"
        return f"{self.plate_number} - {self.model}{driver_info}"


class DriverAssignment(models.Model):
    """Driver to vehicle assignment model."""
    
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DRIVER'},
        related_name='vehicle_assignments'
    )
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='driver_assignments')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'driver_assignments'
        verbose_name = 'Driver Assignment'
        verbose_name_plural = 'Driver Assignments'
        unique_together = ['driver', 'vehicle', 'start_date']
    
    def __str__(self):
        return f"{self.driver.username} -> {self.vehicle.plate_number}"


class Order(models.Model):
    """Order model for LPG delivery requests."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('ON_ROUTE', 'On Route'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CUSTOMER'},
        related_name='orders'
    )
    delivery_address = models.TextField()
    quantity_kg = models.FloatField(validators=[MinValueValidator(0.1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for better tracking
    pickup_address = models.TextField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    special_instructions = models.TextField(blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} ({self.status})"


class Delivery(models.Model):
    """Delivery model tracking order fulfillment."""
    
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DRIVER'},
        related_name='deliveries'
    )
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='deliveries')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['DISPATCHER', 'ADMIN']},
        related_name='assigned_deliveries'
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    
    # Additional tracking fields
    delivery_notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'deliveries'
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"Delivery #{self.id} - Order #{self.order.id} ({self.status})"


class TrackingLog(models.Model):
    """Real-time tracking logs for deliveries."""
    
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='tracking_logs')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Additional tracking data
    speed = models.FloatField(null=True, blank=True)  # km/h
    heading = models.FloatField(null=True, blank=True)  # degrees
    accuracy = models.FloatField(null=True, blank=True)  # meters
    
    class Meta:
        db_table = 'tracking_logs'
        verbose_name = 'Tracking Log'
        verbose_name_plural = 'Tracking Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['delivery', '-timestamp']),
        ]
    
    def __str__(self):
        return f"Tracking #{self.id} - Delivery #{self.delivery.id} at {self.timestamp}"


class Cylinder(models.Model):
    """
    Cylinder model for LPG gas cylinders with QR/RFID tracking.
    
    Security features:
    - Unique QR code and RFID tag with cryptographic validation
    - SHA-256 hash for authenticity verification
    - Tamper detection through scan history
    - Complete lifecycle tracking
    """
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('FILLED', 'Filled'),
        ('IN_DELIVERY', 'In Delivery'),
        ('EMPTY', 'Empty'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('RETIRED', 'Retired'),
        ('STOLEN', 'Stolen/Lost'),
    ]
    
    CYLINDER_TYPE_CHOICES = [
        ('6KG', '6 KG'),
        ('13KG', '13 KG'),
        ('26KG', '26 KG'),
        ('50KG', '50 KG'),
    ]
    
    # Unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial_number = models.CharField(max_length=50, unique=True, db_index=True)
    qr_code = models.CharField(max_length=255, unique=True, db_index=True, editable=False)
    rfid_tag = models.CharField(max_length=255, unique=True, db_index=True, editable=False)
    
    # Security hash for authenticity verification
    auth_hash = models.CharField(max_length=64, editable=False)  # SHA-256 hash
    secret_key = models.CharField(max_length=128, editable=False)  # For generating auth codes
    
    # Cylinder details
    cylinder_type = models.CharField(max_length=10, choices=CYLINDER_TYPE_CHOICES)
    capacity_kg = models.FloatField(validators=[MinValueValidator(0.0)])
    manufacturer = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiry_date = models.DateField()
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    current_customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'CUSTOMER'},
        related_name='cylinders'
    )
    current_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cylinders'
    )
    
    # Location tracking
    last_known_location = models.TextField(blank=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    last_scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scanned_cylinders'
    )
    
    # Maintenance and safety
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    total_fills = models.IntegerField(default=0)
    total_scans = models.IntegerField(default=0)
    
    # Security flags
    is_authentic = models.BooleanField(default=True)
    is_tampered = models.BooleanField(default=False)
    tamper_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cylinders'
        verbose_name = 'Cylinder'
        verbose_name_plural = 'Cylinders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['qr_code']),
            models.Index(fields=['rfid_tag']),
            models.Index(fields=['status', 'cylinder_type']),
            models.Index(fields=['current_customer']),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to generate secure codes on creation."""
        if not self.qr_code:
            # Generate unique QR code
            self.qr_code = f"QR-{uuid.uuid4().hex.upper()[:16]}"
        
        if not self.rfid_tag:
            # Generate unique RFID tag
            self.rfid_tag = f"RFID-{uuid.uuid4().hex.upper()[:16]}"
        
        if not self.secret_key:
            # Generate secret key for auth hash
            self.secret_key = secrets.token_urlsafe(64)
        
        if not self.auth_hash:
            # Generate authentication hash
            data = f"{self.serial_number}{self.qr_code}{self.rfid_tag}{self.secret_key}"
            self.auth_hash = hashlib.sha256(data.encode()).hexdigest()
        
        super().save(*args, **kwargs)
    
    def verify_authenticity(self, code, code_type='qr'):
        """
        Verify cylinder authenticity using QR or RFID code.
        
        Args:
            code: The QR code or RFID tag to verify
            code_type: 'qr' or 'rfid'
        
        Returns:
            tuple: (is_valid, message)
        """
        if code_type == 'qr' and self.qr_code != code:
            return False, "Invalid QR code"
        elif code_type == 'rfid' and self.rfid_tag != code:
            return False, "Invalid RFID tag"
        
        if self.is_tampered:
            return False, "Cylinder shows signs of tampering"
        
        if not self.is_authentic:
            return False, "Cylinder marked as non-authentic"
        
        if self.status == 'RETIRED':
            return False, "Cylinder has been retired"
        
        if self.status == 'STOLEN':
            return False, "Cylinder reported as stolen/lost"
        
        # Check expiry date
        if self.expiry_date < timezone.now().date():
            return False, "Cylinder has expired - requires inspection"
        
        return True, "Cylinder verified successfully"
    
    def generate_auth_token(self):
        """Generate a time-limited authentication token for secure verification."""
        timestamp = str(int(timezone.now().timestamp()))
        data = f"{self.auth_hash}{timestamp}"
        token = hashlib.sha256(data.encode()).hexdigest()
        return f"{token}:{timestamp}"
    
    def __str__(self):
        return f"{self.serial_number} - {self.cylinder_type} ({self.status})"


class CylinderHistory(models.Model):
    """
    Complete history tracking for cylinder lifecycle events.
    
    Tracks all interactions including:
    - Fills and refills
    - Customer deliveries
    - Returns and exchanges
    - Inspections and maintenance
    - Scans and verifications
    - Status changes
    """
    
    EVENT_TYPE_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('FILLED', 'Filled'),
        ('DELIVERED', 'Delivered to Customer'),
        ('RETURNED', 'Returned from Customer'),
        ('SCANNED', 'Scanned'),
        ('INSPECTED', 'Inspected'),
        ('MAINTENANCE', 'Maintenance Performed'),
        ('STATUS_CHANGE', 'Status Changed'),
        ('CUSTOMER_ASSIGNED', 'Assigned to Customer'),
        ('CUSTOMER_UNASSIGNED', 'Unassigned from Customer'),
        ('TAMPER_DETECTED', 'Tamper Detected'),
        ('LOCATION_UPDATE', 'Location Updated'),
    ]
    
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE, related_name='history')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    event_date = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Related entities
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'CUSTOMER'},
        related_name='cylinder_events'
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'DRIVER'},
        related_name='cylinder_deliveries'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cylinder_history'
    )
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cylinder_history'
    )
    
    # Event details
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    location = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Technical details
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_cylinder_events'
    )
    verification_data = models.JSONField(null=True, blank=True)  # Store scan data, GPS, etc.
    
    class Meta:
        db_table = 'cylinder_history'
        verbose_name = 'Cylinder History'
        verbose_name_plural = 'Cylinder Histories'
        ordering = ['-event_date']
        indexes = [
            models.Index(fields=['cylinder', '-event_date']),
            models.Index(fields=['customer', '-event_date']),
            models.Index(fields=['event_type', '-event_date']),
        ]
    
    def __str__(self):
        return f"{self.cylinder.serial_number} - {self.event_type} at {self.event_date}"


class CylinderScan(models.Model):
    """
    Security audit log for all cylinder scan events.
    
    Provides:
    - Complete scan audit trail
    - Suspicious activity detection
    - Rate limiting data
    - Geolocation tracking
    """
    
    SCAN_TYPE_CHOICES = [
        ('QR', 'QR Code Scan'),
        ('RFID', 'RFID Tag Scan'),
        ('MANUAL', 'Manual Entry'),
    ]
    
    SCAN_RESULT_CHOICES = [
        ('SUCCESS', 'Successful Verification'),
        ('FAILED', 'Failed Verification'),
        ('SUSPICIOUS', 'Suspicious Activity'),
        ('TAMPERED', 'Tamper Detected'),
        ('EXPIRED', 'Cylinder Expired'),
        ('STOLEN', 'Reported Stolen'),
    ]
    
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE, related_name='scans')
    scan_type = models.CharField(max_length=10, choices=SCAN_TYPE_CHOICES)
    scan_result = models.CharField(max_length=20, choices=SCAN_RESULT_CHOICES)
    
    # Scanner information
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cylinder_scans'
    )
    scanner_role = models.CharField(max_length=20, blank=True)  # CUSTOMER, DRIVER, DISPATCHER
    
    # Scan details
    scanned_code = models.CharField(max_length=255)
    scan_timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    scan_location_lat = models.FloatField(null=True, blank=True)
    scan_location_lng = models.FloatField(null=True, blank=True)
    scan_location_address = models.TextField(blank=True)
    
    # Security and verification
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    verification_message = models.TextField()
    auth_token = models.CharField(max_length=255, blank=True)
    
    # Suspicious activity flags
    is_suspicious = models.BooleanField(default=False)
    suspicious_reason = models.TextField(blank=True)
    
    # Related context
    related_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cylinder_scans'
    )
    related_delivery = models.ForeignKey(
        Delivery,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cylinder_scans'
    )
    
    class Meta:
        db_table = 'cylinder_scans'
        verbose_name = 'Cylinder Scan'
        verbose_name_plural = 'Cylinder Scans'
        ordering = ['-scan_timestamp']
        indexes = [
            models.Index(fields=['cylinder', '-scan_timestamp']),
            models.Index(fields=['scanned_by', '-scan_timestamp']),
            models.Index(fields=['scan_result', '-scan_timestamp']),
            models.Index(fields=['is_suspicious']),
        ]
    
    def __str__(self):
        return f"{self.cylinder.serial_number} - {self.scan_type} scan at {self.scan_timestamp}"
