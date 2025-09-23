from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, F, ExpressionWrapper, FloatField
from django.utils import timezone
from geopy.distance import geodesic
import logging
import math

from .models import Vehicle, DriverAssignment, Order, Delivery, TrackingLog
from .serializers import (
    VehicleSerializer, DriverAssignmentSerializer, OrderCreateSerializer,
    OrderSerializer, OrderStatusUpdateSerializer, DeliverySerializer,
    DeliveryAssignmentSerializer, TrackingLogSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


class OrderPagination(PageNumberPagination):
    """Custom pagination for orders."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Custom permission classes
class IsCustomerOrReadOnly(permissions.BasePermission):
    """Permission to allow customers to create orders, others to read."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'CUSTOMER'


class IsDispatcherOrAdmin(permissions.BasePermission):
    """Permission for dispatcher and admin roles only."""
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role in ['DISPATCHER', 'ADMIN'])


class IsDriverOrDispatcherOrAdmin(permissions.BasePermission):
    """Permission for driver, dispatcher, and admin roles."""
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role in ['DRIVER', 'DISPATCHER', 'ADMIN'])


# ============= ORDER MANAGEMENT VIEWS =============

@api_view(['POST'])
@permission_classes([IsCustomerOrReadOnly])
def create_order(request):
    """
    Create a new order.
    
    Only customers can create orders. The order will be in PENDING status
    until a driver is assigned.
    """
    try:
        serializer = OrderCreateSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            order = serializer.save()
            
            logger.info(f"Order {order.id} created by customer {request.user.username}")
            
            # Return created order details
            order_serializer = OrderSerializer(order)
            
            return Response({
                'message': 'Order created successfully',
                'order': order_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Order creation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Order creation error: {str(e)}")
        return Response({
            'error': 'Internal server error during order creation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_orders(request):
    """
    List orders based on user role.
    
    - Customers see only their orders
    - Drivers see orders assigned to them
    - Dispatchers and Admins see all orders
    """
    try:
        user = request.user
        
        # Filter orders based on user role
        if user.role == 'CUSTOMER':
            orders = Order.objects.filter(customer=user)
        elif user.role == 'DRIVER':
            orders = Order.objects.filter(delivery__driver=user)
        else:  # DISPATCHER or ADMIN
            orders = Order.objects.all()
        
        # Apply additional filters from query parameters
        status_filter = request.GET.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Pagination
        paginator = OrderPagination()
        page = paginator.paginate_queryset(orders, request)
        
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'orders': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"List orders error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching orders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_order(request, order_id):
    """Get specific order details."""
    try:
        order = Order.objects.get(id=order_id)
        
        # Check permissions
        user = request.user
        if user.role == 'CUSTOMER' and order.customer != user:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'DRIVER':
            if not hasattr(order, 'delivery') or order.delivery.driver != user:
                return Response({
                    'error': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderSerializer(order)
        order_data = serializer.data
        
        # Include delivery information if exists
        if hasattr(order, 'delivery'):
            delivery_serializer = DeliverySerializer(order.delivery)
            order_data['delivery'] = delivery_serializer.data
        
        return Response({
            'order': order_data
        }, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Get order error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching order'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= DRIVER ASSIGNMENT VIEWS =============

def find_nearest_available_driver(delivery_address, exclude_driver_ids=None):
    """
    Find the nearest available driver.
    
    This is a simplified implementation. In production, you would:
    1. Use proper geocoding for addresses
    2. Implement more sophisticated distance calculations
    3. Consider driver workload and vehicle capacity
    4. Use real-time driver location tracking
    """
    
    # Get all active drivers with active vehicle assignments
    current_time = timezone.now()
    
    available_drivers = User.objects.filter(
        role='DRIVER',
        is_active=True,
        vehicle_assignments__end_date__isnull=True,
        vehicle_assignments__vehicle__status='ACTIVE'
    ).exclude(
        id__in=exclude_driver_ids or []
    ).distinct()
    
    # Filter out drivers who are currently on active deliveries
    available_drivers = available_drivers.exclude(
        deliveries__status__in=['ASSIGNED', 'IN_PROGRESS']
    )
    
    if not available_drivers.exists():
        return None, None
    
    # For demo purposes, return the first available driver
    # In production, implement proper distance calculation
    driver = available_drivers.first()
    
    # Get the driver's current vehicle
    current_assignment = DriverAssignment.objects.filter(
        driver=driver,
        end_date__isnull=True,
        vehicle__status='ACTIVE'
    ).first()
    
    return driver, current_assignment.vehicle if current_assignment else None


@api_view(['POST'])
@permission_classes([IsDispatcherOrAdmin])
def assign_driver(request):
    """
    Assign a driver to an order.
    
    Can either specify a specific driver or let the system find the nearest available one.
    """
    try:
        serializer = DeliveryAssignmentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid assignment data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        order_id = validated_data['order_id']
        driver_id = validated_data.get('driver_id')
        vehicle_id = validated_data.get('vehicle_id')
        
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            
            # If specific driver/vehicle not provided, find nearest available
            if not driver_id:
                driver, vehicle = find_nearest_available_driver(order.delivery_address)
                
                if not driver:
                    return Response({
                        'error': 'No available drivers found'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                driver = User.objects.get(id=driver_id)
                if vehicle_id:
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                else:
                    # Find driver's current vehicle assignment
                    current_assignment = DriverAssignment.objects.filter(
                        driver=driver,
                        end_date__isnull=True,
                        vehicle__status='ACTIVE'
                    ).first()
                    
                    if not current_assignment:
                        return Response({
                            'error': 'Driver has no active vehicle assignment'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    vehicle = current_assignment.vehicle
            
            # Create delivery record
            delivery = Delivery.objects.create(
                order=order,
                driver=driver,
                vehicle=vehicle,
                assigned_by=request.user,
                status='ASSIGNED'
            )
            
            # Update order status
            order.status = 'ASSIGNED'
            order.save()
            
            logger.info(f"Order {order.id} assigned to driver {driver.username} by {request.user.username}")
            
            delivery_serializer = DeliverySerializer(delivery)
            
            return Response({
                'message': 'Driver assigned successfully',
                'delivery': delivery_serializer.data
            }, status=status.HTTP_201_CREATED)
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({
            'error': 'Driver not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Vehicle.DoesNotExist:
        return Response({
            'error': 'Vehicle not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Driver assignment error: {str(e)}")
        return Response({
            'error': 'Internal server error during driver assignment'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= STATUS UPDATE VIEWS =============

@api_view(['PATCH'])
@permission_classes([IsDriverOrDispatcherOrAdmin])
def update_order_status(request, order_id):
    """
    Update order status.
    
    - Drivers can update status for their assigned orders
    - Dispatchers and Admins can update any order status
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Check permissions for drivers
        if request.user.role == 'DRIVER':
            if not hasattr(order, 'delivery') or order.delivery.driver != request.user:
                return Response({
                    'error': 'Permission denied - order not assigned to you'
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            with transaction.atomic():
                new_status = serializer.validated_data['status']
                old_status = order.status
                
                # Update order
                order = serializer.save()
                
                # Update delivery status if exists
                if hasattr(order, 'delivery'):
                    delivery = order.delivery
                    
                    if new_status == 'ON_ROUTE' and delivery.status == 'ASSIGNED':
                        delivery.status = 'IN_PROGRESS'
                        delivery.started_at = timezone.now()
                        delivery.save()
                    elif new_status == 'DELIVERED' and delivery.status == 'IN_PROGRESS':
                        delivery.status = 'COMPLETED'
                        delivery.completed_at = timezone.now()
                        delivery.save()
                    elif new_status == 'CANCELLED':
                        delivery.status = 'FAILED'
                        delivery.failure_reason = 'Order cancelled'
                        delivery.save()
                
                logger.info(f"Order {order.id} status updated from {old_status} to {new_status} by {request.user.username}")
                
                order_serializer = OrderSerializer(order)
                
                return Response({
                    'message': 'Order status updated successfully',
                    'order': order_serializer.data
                }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Status update failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Status update error: {str(e)}")
        return Response({
            'error': 'Internal server error during status update'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= TRACKING VIEWS =============

@api_view(['POST'])
@permission_classes([IsDriverOrDispatcherOrAdmin])
def add_tracking_log(request):
    """
    Add tracking log for delivery.
    
    Drivers can add tracking logs for their assigned deliveries.
    """
    try:
        # Get delivery ID from request
        delivery_id = request.data.get('delivery')
        
        if not delivery_id:
            return Response({
                'error': 'Delivery ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        delivery = Delivery.objects.get(id=delivery_id)
        
        # Check permissions for drivers
        if request.user.role == 'DRIVER' and delivery.driver != request.user:
            return Response({
                'error': 'Permission denied - delivery not assigned to you'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TrackingLogSerializer(data=request.data)
        
        if serializer.is_valid():
            tracking_log = serializer.save()
            
            return Response({
                'message': 'Tracking log added successfully',
                'tracking_log': TrackingLogSerializer(tracking_log).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Invalid tracking data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Delivery.DoesNotExist:
        return Response({
            'error': 'Delivery not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Tracking log error: {str(e)}")
        return Response({
            'error': 'Internal server error while adding tracking log'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_delivery_tracking(request, delivery_id):
    """
    Get tracking logs for a delivery.
    
    Customers can track their orders, drivers can see their delivery tracking.
    """
    try:
        delivery = Delivery.objects.get(id=delivery_id)
        
        # Check permissions
        user = request.user
        if user.role == 'CUSTOMER' and delivery.order.customer != user:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'DRIVER' and delivery.driver != user:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        tracking_logs = TrackingLog.objects.filter(delivery=delivery).order_by('-timestamp')
        
        serializer = TrackingLogSerializer(tracking_logs, many=True)
        
        return Response({
            'delivery_id': delivery_id,
            'tracking_logs': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Delivery.DoesNotExist:
        return Response({
            'error': 'Delivery not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Get tracking error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching tracking data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
