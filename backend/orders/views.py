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

from .models import (
    Vehicle, DriverAssignment, Order, Delivery, TrackingLog,
    Cylinder, CylinderHistory, CylinderScan
)
from .serializers import (
    VehicleSerializer, VehicleCreateSerializer, VehicleDriverAssignmentSerializer,
    DriverAssignmentSerializer, OrderCreateSerializer,
    OrderSerializer, OrderStatusUpdateSerializer, DeliverySerializer,
    DeliveryAssignmentSerializer, TrackingLogSerializer,
    CylinderSerializer, CylinderCreateSerializer, CylinderScanSerializer,
    CylinderHistorySerializer, CylinderScanLogSerializer,
    CylinderAssignmentSerializer, CylinderStatusUpdateSerializer
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


# ============= VEHICLE MANAGEMENT VIEWS =============

@api_view(['POST'])
@permission_classes([IsDispatcherOrAdmin])
def create_vehicle(request):
    """
    Create a new vehicle.
    
    Only dispatchers and admins can create vehicles.
    """
    try:
        serializer = VehicleCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            vehicle = serializer.save()
            
            logger.info(f"Vehicle {vehicle.plate_number} created by {request.user.username}")
            
            # Return created vehicle details
            vehicle_serializer = VehicleSerializer(vehicle)
            
            return Response({
                'message': 'Vehicle created successfully',
                'vehicle': vehicle_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Vehicle creation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Vehicle creation error: {str(e)}")
        return Response({
            'error': 'Internal server error during vehicle creation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_vehicles(request):
    """
    List all vehicles.
    
    All authenticated users can view vehicles.
    """
    try:
        vehicles = Vehicle.objects.all().select_related('driver')
        
        # Apply filters from query parameters
        status_filter = request.GET.get('status')
        if status_filter:
            vehicles = vehicles.filter(status=status_filter)
        
        available_only = request.GET.get('available_only')
        if available_only and available_only.lower() == 'true':
            vehicles = vehicles.filter(driver__isnull=True, status='ACTIVE')
        
        # Pagination
        paginator = OrderPagination()
        page = paginator.paginate_queryset(vehicles, request)
        
        if page is not None:
            serializer = VehicleSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = VehicleSerializer(vehicles, many=True)
        return Response({
            'vehicles': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"List vehicles error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching vehicles'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_vehicle(request, vehicle_id):
    """Get specific vehicle details."""
    try:
        vehicle = Vehicle.objects.select_related('driver').get(id=vehicle_id)
        
        serializer = VehicleSerializer(vehicle)
        
        return Response({
            'vehicle': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Vehicle.DoesNotExist:
        return Response({
            'error': 'Vehicle not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Get vehicle error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching vehicle'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsDispatcherOrAdmin])
def update_vehicle(request, vehicle_id):
    """
    Update vehicle details.
    
    Only dispatchers and admins can update vehicles.
    """
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        serializer = VehicleCreateSerializer(vehicle, data=request.data, partial=True)
        
        if serializer.is_valid():
            vehicle = serializer.save()
            
            logger.info(f"Vehicle {vehicle.plate_number} updated by {request.user.username}")
            
            vehicle_serializer = VehicleSerializer(vehicle)
            
            return Response({
                'message': 'Vehicle updated successfully',
                'vehicle': vehicle_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Vehicle update failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Vehicle.DoesNotExist:
        return Response({
            'error': 'Vehicle not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Vehicle update error: {str(e)}")
        return Response({
            'error': 'Internal server error during vehicle update'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsDispatcherOrAdmin])
def assign_driver_to_vehicle(request):
    """
    Assign or unassign a driver to a vehicle.
    
    Only dispatchers and admins can assign drivers to vehicles.
    """
    try:
        serializer = VehicleDriverAssignmentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid assignment data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        vehicle_id = validated_data['vehicle_id']
        driver_id = validated_data.get('driver_id')
        
        with transaction.atomic():
            vehicle = Vehicle.objects.select_for_update().get(id=vehicle_id)
            
            # If driver_id is None, unassign current driver
            if driver_id is None:
                old_driver = vehicle.driver
                vehicle.driver = None
                vehicle.save()
                
                message = f"Driver unassigned from vehicle {vehicle.plate_number}"
                if old_driver:
                    logger.info(f"Driver {old_driver.username} unassigned from vehicle {vehicle.plate_number} by {request.user.username}")
                else:
                    logger.info(f"Vehicle {vehicle.plate_number} had no assigned driver")
            else:
                # Assign new driver
                driver = User.objects.get(id=driver_id)
                
                # Unassign driver from any previous vehicle
                try:
                    old_vehicle = Vehicle.objects.get(driver=driver)
                    old_vehicle.driver = None
                    old_vehicle.save()
                    logger.info(f"Driver {driver.username} reassigned from vehicle {old_vehicle.plate_number} to {vehicle.plate_number}")
                except Vehicle.DoesNotExist:
                    # Driver was not assigned to any vehicle
                    pass
                
                # Assign to new vehicle
                vehicle.driver = driver
                vehicle.save()
                
                message = f"Driver {driver.username} assigned to vehicle {vehicle.plate_number}"
                logger.info(f"Driver {driver.username} assigned to vehicle {vehicle.plate_number} by {request.user.username}")
            
            # Return updated vehicle details
            vehicle_serializer = VehicleSerializer(vehicle)
            
            return Response({
                'message': message,
                'vehicle': vehicle_serializer.data
            }, status=status.HTTP_200_OK)
        
    except Vehicle.DoesNotExist:
        return Response({
            'error': 'Vehicle not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({
            'error': 'Driver not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Driver-vehicle assignment error: {str(e)}")
        return Response({
            'error': 'Internal server error during driver-vehicle assignment'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= CYLINDER MANAGEMENT VIEWS =============

@api_view(['POST'])
@permission_classes([IsDispatcherOrAdmin])
def register_cylinder(request):
    """
    Register a new cylinder with QR/RFID codes.
    
    Only dispatchers and admins can register cylinders.
    Automatically generates secure QR codes, RFID tags, and authentication hashes.
    """
    try:
        serializer = CylinderCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                # Create cylinder (codes generated automatically in model)
                cylinder = serializer.save()
                
                # Create registration history entry
                CylinderHistory.objects.create(
                    cylinder=cylinder,
                    event_type='REGISTERED',
                    performed_by=request.user,
                    notes=f"Cylinder registered by {request.user.username}"
                )
                
                logger.info(f"Cylinder {cylinder.serial_number} registered by {request.user.username}")
                
                # Return cylinder details including generated codes
                cylinder_serializer = CylinderSerializer(cylinder)
                
                return Response({
                    'message': 'Cylinder registered successfully',
                    'cylinder': cylinder_serializer.data,
                    'security': {
                        'qr_code': cylinder.qr_code,
                        'rfid_tag': cylinder.rfid_tag,
                        'auth_token': cylinder.generate_auth_token()
                    }
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Cylinder registration failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Cylinder registration error: {str(e)}")
        return Response({
            'error': 'Internal server error during cylinder registration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def scan_cylinder(request):
    """
    Scan and verify cylinder authenticity using QR code or RFID tag.
    
    Features:
    - Real-time authenticity verification
    - Tamper detection
    - Scan history logging
    - Suspicious activity detection
    - GPS location tracking
    
    Available to all authenticated users.
    """
    try:
        serializer = CylinderScanSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid scan data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        code = validated_data['code']
        scan_type = validated_data['scan_type']
        
        # Find cylinder by code
        try:
            if scan_type == 'QR':
                cylinder = Cylinder.objects.get(qr_code=code)
            elif scan_type == 'RFID':
                cylinder = Cylinder.objects.get(rfid_tag=code)
            else:
                # Manual entry - try both
                cylinder = Cylinder.objects.filter(
                    models.Q(qr_code=code) | models.Q(rfid_tag=code)
                ).first()
                
                if not cylinder:
                    return Response({
                        'error': 'Cylinder not found',
                        'scan_result': 'FAILED',
                        'verified': False
                    }, status=status.HTTP_404_NOT_FOUND)
        
        except Cylinder.DoesNotExist:
            # Log failed scan attempt
            logger.warning(f"Failed scan attempt by {request.user.username}: code {code}")
            
            return Response({
                'error': 'Cylinder not found',
                'scan_result': 'FAILED',
                'verified': False,
                'message': 'Invalid QR/RFID code'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify authenticity
        is_valid, message = cylinder.verify_authenticity(code, scan_type.lower())
        
        # Determine scan result
        if is_valid:
            scan_result = 'SUCCESS'
        elif cylinder.is_tampered:
            scan_result = 'TAMPERED'
        elif cylinder.status == 'STOLEN':
            scan_result = 'STOLEN'
        elif cylinder.expiry_date < timezone.now().date():
            scan_result = 'EXPIRED'
        else:
            scan_result = 'FAILED'
        
        # Detect suspicious activity
        is_suspicious = False
        suspicious_reason = ''
        
        # Check for rapid repeated scans (potential cloning attempt)
        recent_scans = CylinderScan.objects.filter(
            cylinder=cylinder,
            scan_timestamp__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).count()
        
        if recent_scans > 5:
            is_suspicious = True
            suspicious_reason = 'Multiple rapid scans detected - possible cloning attempt'
        
        # Check for scans from different locations in short time
        if validated_data.get('location_lat') and validated_data.get('location_lng'):
            last_scan = CylinderScan.objects.filter(
                cylinder=cylinder,
                scan_location_lat__isnull=False
            ).first()
            
            if last_scan:
                time_diff = (timezone.now() - last_scan.scan_timestamp).total_seconds()
                if time_diff < 300:  # 5 minutes
                    # Calculate distance (simplified)
                    lat_diff = abs(validated_data['location_lat'] - last_scan.scan_location_lat)
                    lng_diff = abs(validated_data['location_lng'] - last_scan.scan_location_lng)
                    
                    # If moved more than ~50km in 5 minutes (very rough estimate)
                    if lat_diff > 0.5 or lng_diff > 0.5:
                        is_suspicious = True
                        suspicious_reason += ' Impossible location change detected.'
        
        with transaction.atomic():
            # Create scan log
            scan_log = CylinderScan.objects.create(
                cylinder=cylinder,
                scan_type=scan_type,
                scan_result=scan_result,
                scanned_by=request.user,
                scanner_role=request.user.role,
                scanned_code=code,
                scan_location_lat=validated_data.get('location_lat'),
                scan_location_lng=validated_data.get('location_lng'),
                scan_location_address=validated_data.get('location_address', ''),
                verification_message=message,
                auth_token=cylinder.generate_auth_token() if is_valid else '',
                is_suspicious=is_suspicious,
                suspicious_reason=suspicious_reason,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                related_order_id=validated_data.get('order_id')
            )
            
            # Update cylinder last scan info
            cylinder.last_scanned_at = timezone.now()
            cylinder.last_scanned_by = request.user
            cylinder.total_scans += 1
            
            if validated_data.get('location_address'):
                cylinder.last_known_location = validated_data['location_address']
            
            cylinder.save()
            
            # Create history entry
            CylinderHistory.objects.create(
                cylinder=cylinder,
                event_type='SCANNED',
                performed_by=request.user,
                location=validated_data.get('location_address', ''),
                notes=f"{scan_type} scan - {message}",
                verification_data={
                    'scan_result': scan_result,
                    'is_suspicious': is_suspicious,
                    'latitude': validated_data.get('location_lat'),
                    'longitude': validated_data.get('location_lng')
                }
            )
            
            logger.info(
                f"Cylinder {cylinder.serial_number} scanned by {request.user.username} - "
                f"Result: {scan_result}, Suspicious: {is_suspicious}"
            )
        
        # Build response
        response_data = {
            'verified': is_valid,
            'scan_result': scan_result,
            'message': message,
            'cylinder': {
                'serial_number': cylinder.serial_number,
                'cylinder_type': cylinder.cylinder_type,
                'capacity_kg': cylinder.capacity_kg,
                'status': cylinder.status,
                'manufacturer': cylinder.manufacturer,
                'expiry_date': cylinder.expiry_date.isoformat(),
                'total_fills': cylinder.total_fills,
                'last_inspection_date': cylinder.last_inspection_date.isoformat() if cylinder.last_inspection_date else None,
            },
            'security': {
                'is_authentic': cylinder.is_authentic,
                'is_tampered': cylinder.is_tampered,
                'is_expired': cylinder.expiry_date < timezone.now().date(),
                'auth_token': cylinder.generate_auth_token() if is_valid else None
            }
        }
        
        if is_suspicious:
            response_data['warning'] = {
                'is_suspicious': True,
                'reason': suspicious_reason,
                'action': 'Report to security team immediately'
            }
        
        if cylinder.current_customer:
            response_data['customer'] = {
                'name': cylinder.current_customer.username,
                'email': cylinder.current_customer.email,
            }
        
        if cylinder.current_order:
            response_data['order'] = {
                'id': cylinder.current_order.id,
                'status': cylinder.current_order.status,
            }
        
        status_code = status.HTTP_200_OK if is_valid else status.HTTP_200_OK
        
        return Response(response_data, status=status_code)
        
    except Exception as e:
        logger.error(f"Cylinder scan error: {str(e)}")
        return Response({
            'error': 'Internal server error during cylinder scan'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cylinder_history(request, cylinder_id):
    """
    Get complete history for a cylinder.
    
    Shows all events including:
    - Registration
    - Fills and refills
    - Customer assignments
    - Deliveries
    - Scans
    - Inspections
    - Status changes
    
    Permissions:
    - Customers can view history of their cylinders
    - Drivers can view cylinders in their deliveries
    - Dispatchers and admins can view all
    """
    try:
        cylinder = Cylinder.objects.get(id=cylinder_id)
        
        # Check permissions
        user = request.user
        if user.role == 'CUSTOMER':
            if cylinder.current_customer != user:
                # Check if customer ever had this cylinder
                has_history = CylinderHistory.objects.filter(
                    cylinder=cylinder,
                    customer=user
                ).exists()
                
                if not has_history:
                    return Response({
                        'error': 'Permission denied'
                    }, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'DRIVER':
            # Check if driver has delivered this cylinder
            has_delivered = CylinderHistory.objects.filter(
                cylinder=cylinder,
                driver=user
            ).exists()
            
            if not has_delivered:
                return Response({
                    'error': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Get history
        history = CylinderHistory.objects.filter(cylinder=cylinder)
        
        # Apply filters
        event_type = request.GET.get('event_type')
        if event_type:
            history = history.filter(event_type=event_type)
        
        start_date = request.GET.get('start_date')
        if start_date:
            history = history.filter(event_date__gte=start_date)
        
        end_date = request.GET.get('end_date')
        if end_date:
            history = history.filter(event_date__lte=end_date)
        
        # Pagination
        paginator = OrderPagination()
        page = paginator.paginate_queryset(history, request)
        
        if page is not None:
            serializer = CylinderHistorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = CylinderHistorySerializer(history, many=True)
        cylinder_serializer = CylinderSerializer(cylinder)
        
        return Response({
            'cylinder': cylinder_serializer.data,
            'history': serializer.data,
            'total_events': history.count()
        }, status=status.HTTP_200_OK)
        
    except Cylinder.DoesNotExist:
        return Response({
            'error': 'Cylinder not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Get cylinder history error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching cylinder history'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsDispatcherOrAdmin])
def assign_cylinder_to_order(request):
    """
    Assign a cylinder to an order/customer.
    
    Creates proper tracking in cylinder history.
    Only dispatchers and admins can assign cylinders.
    """
    try:
        serializer = CylinderAssignmentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid assignment data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        cylinder_id = validated_data['cylinder_id']
        order_id = validated_data.get('order_id')
        customer_id = validated_data.get('customer_id')
        notes = validated_data.get('notes', '')
        
        with transaction.atomic():
            cylinder = Cylinder.objects.select_for_update().get(id=cylinder_id)
            
            # Update cylinder
            previous_customer = cylinder.current_customer
            previous_order = cylinder.current_order
            
            if order_id:
                order = Order.objects.get(id=order_id)
                cylinder.current_order = order
                cylinder.current_customer = order.customer
                cylinder.status = 'IN_DELIVERY'
                
                # Create history entry
                CylinderHistory.objects.create(
                    cylinder=cylinder,
                    event_type='DELIVERED',
                    customer=order.customer,
                    order=order,
                    performed_by=request.user,
                    previous_status=cylinder.status,
                    new_status='IN_DELIVERY',
                    notes=notes or f"Assigned to order #{order.id}"
                )
                
            elif customer_id:
                customer = User.objects.get(id=customer_id)
                cylinder.current_customer = customer
                cylinder.current_order = None
                
                # Create history entry
                CylinderHistory.objects.create(
                    cylinder=cylinder,
                    event_type='CUSTOMER_ASSIGNED',
                    customer=customer,
                    performed_by=request.user,
                    notes=notes or f"Assigned to customer {customer.username}"
                )
            
            cylinder.save()
            
            logger.info(
                f"Cylinder {cylinder.serial_number} assigned by {request.user.username}"
            )
            
            cylinder_serializer = CylinderSerializer(cylinder)
            
            return Response({
                'message': 'Cylinder assigned successfully',
                'cylinder': cylinder_serializer.data
            }, status=status.HTTP_200_OK)
        
    except Cylinder.DoesNotExist:
        return Response({
            'error': 'Cylinder not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Cylinder assignment error: {str(e)}")
        return Response({
            'error': 'Internal server error during cylinder assignment'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_cylinders(request):
    """
    List cylinders based on user role and filters.
    
    - Customers see only their cylinders
    - Drivers see cylinders in their deliveries
    - Dispatchers and admins see all cylinders
    """
    try:
        user = request.user
        
        # Filter cylinders based on user role
        if user.role == 'CUSTOMER':
            cylinders = Cylinder.objects.filter(current_customer=user)
        elif user.role == 'DRIVER':
            # Get cylinders from driver's current deliveries
            delivery_orders = Order.objects.filter(delivery__driver=user)
            cylinders = Cylinder.objects.filter(current_order__in=delivery_orders)
        else:  # DISPATCHER or ADMIN
            cylinders = Cylinder.objects.all()
        
        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter:
            cylinders = cylinders.filter(status=status_filter)
        
        cylinder_type = request.GET.get('cylinder_type')
        if cylinder_type:
            cylinders = cylinders.filter(cylinder_type=cylinder_type)
        
        is_tampered = request.GET.get('is_tampered')
        if is_tampered and is_tampered.lower() == 'true':
            cylinders = cylinders.filter(is_tampered=True)
        
        is_expired = request.GET.get('is_expired')
        if is_expired and is_expired.lower() == 'true':
            cylinders = cylinders.filter(expiry_date__lt=timezone.now().date())
        
        # Pagination
        paginator = OrderPagination()
        page = paginator.paginate_queryset(cylinders, request)
        
        if page is not None:
            serializer = CylinderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = CylinderSerializer(cylinders, many=True)
        return Response({
            'cylinders': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"List cylinders error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching cylinders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cylinder(request, cylinder_id):
    """Get specific cylinder details with full history."""
    try:
        cylinder = Cylinder.objects.get(id=cylinder_id)
        
        # Check permissions
        user = request.user
        if user.role == 'CUSTOMER' and cylinder.current_customer != user:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'DRIVER':
            # Check if in driver's deliveries
            has_delivery = Order.objects.filter(
                delivery__driver=user,
                cylinders=cylinder
            ).exists()
            
            if not has_delivery:
                return Response({
                    'error': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CylinderSerializer(cylinder)
        
        # Include recent history
        recent_history = CylinderHistory.objects.filter(
            cylinder=cylinder
        )[:10]
        history_serializer = CylinderHistorySerializer(recent_history, many=True)
        
        # Include recent scans
        recent_scans = CylinderScan.objects.filter(
            cylinder=cylinder
        )[:5]
        scans_serializer = CylinderScanLogSerializer(recent_scans, many=True)
        
        return Response({
            'cylinder': serializer.data,
            'recent_history': history_serializer.data,
            'recent_scans': scans_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Cylinder.DoesNotExist:
        return Response({
            'error': 'Cylinder not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Get cylinder error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching cylinder'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsDispatcherOrAdmin])
def update_cylinder_status(request, cylinder_id):
    """
    Update cylinder status.
    
    Only dispatchers and admins can update cylinder status.
    Creates history entry for audit trail.
    """
    try:
        cylinder = Cylinder.objects.get(id=cylinder_id)
        
        serializer = CylinderStatusUpdateSerializer(
            data=request.data,
            context={'cylinder': cylinder}
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                validated_data = serializer.validated_data
                new_status = validated_data['status']
                old_status = cylinder.status
                notes = validated_data.get('notes', '')
                location = validated_data.get('location', '')
                
                # Update cylinder
                cylinder.status = new_status
                
                if location:
                    cylinder.last_known_location = location
                
                cylinder.save()
                
                # Create history entry
                CylinderHistory.objects.create(
                    cylinder=cylinder,
                    event_type='STATUS_CHANGE',
                    performed_by=request.user,
                    previous_status=old_status,
                    new_status=new_status,
                    location=location,
                    notes=notes or f"Status changed from {old_status} to {new_status}"
                )
                
                logger.info(
                    f"Cylinder {cylinder.serial_number} status updated from "
                    f"{old_status} to {new_status} by {request.user.username}"
                )
                
                cylinder_serializer = CylinderSerializer(cylinder)
                
                return Response({
                    'message': 'Cylinder status updated successfully',
                    'cylinder': cylinder_serializer.data
                }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Status update failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Cylinder.DoesNotExist:
        return Response({
            'error': 'Cylinder not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Cylinder status update error: {str(e)}")
        return Response({
            'error': 'Internal server error during cylinder status update'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
