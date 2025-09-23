from django.contrib import admin
from .models import Vehicle, DriverAssignment, Order, Delivery, TrackingLog


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
