from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order management
    path('orders/', views.list_orders, name='list_orders'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/', views.get_order, name='get_order'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    
    # Driver assignment
    path('orders/assign-driver/', views.assign_driver, name='assign_driver'),
    
    # Vehicle management
    path('vehicles/', views.list_vehicles, name='list_vehicles'),
    path('vehicles/create/', views.create_vehicle, name='create_vehicle'),
    path('vehicles/<int:vehicle_id>/', views.get_vehicle, name='get_vehicle'),
    path('vehicles/<int:vehicle_id>/update/', views.update_vehicle, name='update_vehicle'),
    path('vehicles/assign-driver/', views.assign_driver_to_vehicle, name='assign_driver_to_vehicle'),
    
    # Tracking
    path('tracking/', views.add_tracking_log, name='add_tracking_log'),
    path('tracking/<int:delivery_id>/', views.get_delivery_tracking, name='get_delivery_tracking'),
]