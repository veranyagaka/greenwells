from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


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
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.plate_number} - {self.model}"


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
