from django.contrib import admin
from .models import (
    Vehicle, DriverAssignment, Order, Delivery, TrackingLog,
    Cylinder, CylinderHistory, CylinderScan
)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'model', 'capacity_kg', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['plate_number', 'model']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    list_display = ['driver', 'vehicle', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['driver__username', 'vehicle__plate_number']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'delivery_address', 'quantity_kg', 'status', 'scheduled_time', 'created_at']
    list_filter = ['status', 'created_at', 'scheduled_time']
    search_fields = ['customer__username', 'customer__email', 'delivery_address']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'driver', 'vehicle', 'status', 'assigned_at', 'completed_at']
    list_filter = ['status', 'assigned_at', 'started_at', 'completed_at']
    search_fields = ['order__id', 'driver__username', 'vehicle__plate_number']
    readonly_fields = ['assigned_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'driver', 'vehicle', 'assigned_by')


@admin.register(TrackingLog)
class TrackingLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'delivery', 'latitude', 'longitude', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['delivery__id']
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery__order')


@admin.register(Cylinder)
class CylinderAdmin(admin.ModelAdmin):
    list_display = [
        'serial_number', 'qr_code', 'cylinder_type', 'status',
        'current_customer', 'is_authentic', 'is_tampered', 'expiry_date'
    ]
    list_filter = ['status', 'cylinder_type', 'is_authentic', 'is_tampered', 'expiry_date']
    search_fields = ['serial_number', 'qr_code', 'rfid_tag', 'manufacturer']
    readonly_fields = ['id', 'qr_code', 'rfid_tag', 'auth_hash', 'secret_key', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'serial_number', 'qr_code', 'rfid_tag')
        }),
        ('Cylinder Details', {
            'fields': ('cylinder_type', 'capacity_kg', 'manufacturer', 'manufacturing_date', 'expiry_date')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'current_customer', 'current_order', 'last_known_location')
        }),
        ('Maintenance', {
            'fields': ('last_inspection_date', 'next_inspection_date', 'total_fills', 'total_scans')
        }),
        ('Security', {
            'fields': ('is_authentic', 'is_tampered', 'tamper_notes', 'auth_hash', 'secret_key')
        }),
        ('Timestamps', {
            'fields': ('last_scanned_at', 'last_scanned_by', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('current_customer', 'current_order')


@admin.register(CylinderHistory)
class CylinderHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cylinder', 'event_type', 'event_date',
        'customer', 'driver', 'performed_by'
    ]
    list_filter = ['event_type', 'event_date']
    search_fields = ['cylinder__serial_number', 'customer__username', 'notes']
    readonly_fields = ['event_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cylinder', 'customer', 'driver', 'order', 'delivery', 'performed_by'
        )


@admin.register(CylinderScan)
class CylinderScanAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cylinder', 'scan_type', 'scan_result',
        'scanned_by', 'scan_timestamp', 'is_suspicious'
    ]
    list_filter = ['scan_type', 'scan_result', 'is_suspicious', 'scan_timestamp']
    search_fields = ['cylinder__serial_number', 'scanned_by__username', 'scanned_code']
    readonly_fields = ['scan_timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cylinder', 'scanned_by', 'related_order', 'related_delivery'
        )
