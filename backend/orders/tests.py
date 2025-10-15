from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
import json

from .models import Vehicle, DriverAssignment, Order, Delivery, TrackingLog
from users.jwt_service import JWTService

User = get_user_model()


class OrdersModelTestCase(TestCase):
    """Test cases for Orders app models."""
    
    def setUp(self):
        self.customer = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123',
            role='CUSTOMER'
        )
        self.driver = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            role='DRIVER'
        )
        self.dispatcher = User.objects.create_user(
            username='testdispatcher',
            email='dispatcher@test.com',
            password='testpass123',
            role='DISPATCHER'
        )
        
        self.vehicle = Vehicle.objects.create(
            plate_number='TEST-123',
            model='Toyota Hiace',
            capacity_kg=500.0,
            status='ACTIVE'
        )
        
        self.driver_assignment = DriverAssignment.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            start_date=timezone.now()
        )
    
    def test_vehicle_creation(self):
        """Test vehicle model creation."""
        self.assertEqual(str(self.vehicle), "TEST-123 - Toyota Hiace - Unassigned")
        self.assertEqual(self.vehicle.status, 'ACTIVE')
        self.assertEqual(self.vehicle.capacity_kg, 500.0)
    
    def test_order_creation(self):
        """Test order model creation."""
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2)
        )
        
        self.assertEqual(order.status, 'PENDING')
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.quantity_kg, 25.0)
    
    def test_delivery_creation(self):
        """Test delivery model creation."""
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2)
        )
        
        delivery = Delivery.objects.create(
            order=order,
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_by=self.dispatcher
        )
        
        self.assertEqual(delivery.status, 'ASSIGNED')
        self.assertEqual(delivery.driver, self.driver)
        self.assertEqual(delivery.order, order)


class OrderAPITestCase(APITestCase):
    """Test cases for Orders API endpoints."""
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123',
            role='CUSTOMER'
        )
        self.driver = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            role='DRIVER'
        )
        self.dispatcher = User.objects.create_user(
            username='testdispatcher',
            email='dispatcher@test.com',
            password='testpass123',
            role='DISPATCHER'
        )
        
        # Create test vehicle and assignment
        self.vehicle = Vehicle.objects.create(
            plate_number='TEST-123',
            model='Toyota Hiace',
            capacity_kg=500.0,
            status='ACTIVE'
        )
        
        self.driver_assignment = DriverAssignment.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            start_date=timezone.now()
        )
        
        # Generate JWT tokens
        self.customer_tokens = JWTService.generate_token_pair(self.customer)
        self.driver_tokens = JWTService.generate_token_pair(self.driver)
        self.dispatcher_tokens = JWTService.generate_token_pair(self.dispatcher)
    
    def get_auth_header(self, tokens):
        """Helper method to get authorization header."""
        return f"Bearer {tokens['access_token']}"
    
    def test_create_order_success(self):
        """Test successful order creation by customer."""
        url = reverse('orders:create_order')
        data = {
            'delivery_address': '123 Test Street, Test City',
            'quantity_kg': 25.0,
            'scheduled_time': (timezone.now() + timedelta(hours=2)).isoformat(),
            'customer_phone': '+1234567890',
            'special_instructions': 'Call when arriving'
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order', response.data)
        self.assertEqual(response.data['order']['customer'], self.customer.id)
        self.assertEqual(response.data['order']['status'], 'PENDING')
    
    def test_create_order_permission_denied(self):
        """Test order creation permission denied for non-customers."""
        url = reverse('orders:create_order')
        data = {
            'delivery_address': '123 Test Street',
            'quantity_kg': 25.0,
            'scheduled_time': (timezone.now() + timedelta(hours=2)).isoformat()
        }
        
        # Try with driver token
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.driver_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_order_validation_errors(self):
        """Test order creation validation errors."""
        url = reverse('orders:create_order')
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        # Test with invalid quantity
        data = {
            'delivery_address': '123 Test Street',
            'quantity_kg': -5.0,  # Invalid negative quantity
            'scheduled_time': (timezone.now() + timedelta(hours=2)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with past scheduled time
        data = {
            'delivery_address': '123 Test Street',
            'quantity_kg': 25.0,
            'scheduled_time': (timezone.now() - timedelta(hours=1)).isoformat()  # Past time
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_orders_customer(self):
        """Test listing orders for customer."""
        # Create a test order
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2)
        )
        
        url = reverse('orders:list_orders')
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], order.id)
    
    def test_assign_driver_success(self):
        """Test successful driver assignment by dispatcher."""
        # Create a test order
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2)
        )
        
        url = reverse('orders:assign_driver')
        data = {
            'order_id': order.id,
            'driver_id': self.driver.id,
            'vehicle_id': self.vehicle.id
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('delivery', response.data)
        
        # Verify order status updated
        order.refresh_from_db()
        self.assertEqual(order.status, 'ASSIGNED')
    
    def test_assign_driver_permission_denied(self):
        """Test driver assignment permission denied for customers."""
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2)
        )
        
        url = reverse('orders:assign_driver')
        data = {
            'order_id': order.id,
            'driver_id': self.driver.id
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_order_status(self):
        """Test order status update."""
        # Create order and delivery
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2),
            status='ASSIGNED'
        )
        
        delivery = Delivery.objects.create(
            order=order,
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_by=self.dispatcher
        )
        
        url = reverse('orders:update_order_status', kwargs={'order_id': order.id})
        data = {'status': 'ON_ROUTE'}
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.driver_tokens)
        )
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status updated
        order.refresh_from_db()
        delivery.refresh_from_db()
        self.assertEqual(order.status, 'ON_ROUTE')
        self.assertEqual(delivery.status, 'IN_PROGRESS')
    
    def test_add_tracking_log(self):
        """Test adding tracking log."""
        # Create order and delivery
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2)
        )
        
        delivery = Delivery.objects.create(
            order=order,
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_by=self.dispatcher
        )
        
        url = reverse('orders:add_tracking_log')
        data = {
            'delivery': delivery.id,
            'latitude': -1.2921,
            'longitude': 36.8219,
            'speed': 25.5
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.driver_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tracking_log', response.data)
        
        # Verify tracking log created
        tracking_log = TrackingLog.objects.get(delivery=delivery)
        self.assertEqual(tracking_log.latitude, -1.2921)
        self.assertEqual(tracking_log.longitude, 36.8219)
    
    def test_invalid_status_transition(self):
        """Test invalid status transition."""
        order = Order.objects.create(
            customer=self.customer,
            delivery_address='123 Test Street',
            quantity_kg=25.0,
            scheduled_time=timezone.now() + timedelta(hours=2),
            status='DELIVERED'  # Final status
        )
        
        url = reverse('orders:update_order_status', kwargs={'order_id': order.id})
        data = {'status': 'ON_ROUTE'}  # Invalid transition from DELIVERED
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class VehicleAPITestCase(APITestCase):
    """Test cases for Vehicle management API endpoints."""
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123',
            role='CUSTOMER'
        )
        self.driver = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            role='DRIVER'
        )
        self.dispatcher = User.objects.create_user(
            username='testdispatcher',
            email='dispatcher@test.com',
            password='testpass123',
            role='DISPATCHER'
        )
        
        # Generate JWT tokens
        self.customer_tokens = JWTService.generate_token_pair(self.customer)
        self.driver_tokens = JWTService.generate_token_pair(self.driver)
        self.dispatcher_tokens = JWTService.generate_token_pair(self.dispatcher)
    
    def get_auth_header(self, tokens):
        """Helper method to get authorization header."""
        return f"Bearer {tokens['access_token']}"
    
    def test_create_vehicle_success(self):
        """Test successful vehicle creation by dispatcher."""
        url = reverse('orders:create_vehicle')
        data = {
            'plate_number': 'KCA-123A',
            'model': 'Toyota Hiace',
            'capacity_kg': 750.0,
            'status': 'ACTIVE'
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('vehicle', response.data)
        self.assertEqual(response.data['vehicle']['plate_number'], 'KCA-123A')
        self.assertEqual(response.data['vehicle']['model'], 'Toyota Hiace')
    
    def test_create_vehicle_permission_denied(self):
        """Test vehicle creation permission denied for customers."""
        url = reverse('orders:create_vehicle')
        data = {
            'plate_number': 'KCA-123A',
            'model': 'Toyota Hiace',
            'capacity_kg': 750.0
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_vehicle_validation_errors(self):
        """Test vehicle creation validation errors."""
        url = reverse('orders:create_vehicle')
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        # Test with invalid capacity
        data = {
            'plate_number': 'KCA-123A',
            'model': 'Toyota Hiace',
            'capacity_kg': -100.0  # Invalid negative capacity
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with short plate number
        data = {
            'plate_number': 'AB',  # Too short
            'model': 'Toyota Hiace',
            'capacity_kg': 750.0
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_vehicles(self):
        """Test listing vehicles."""
        # Create test vehicles
        vehicle1 = Vehicle.objects.create(
            plate_number='KCA-123A',
            model='Toyota Hiace',
            capacity_kg=750.0,
            status='ACTIVE'
        )
        vehicle2 = Vehicle.objects.create(
            plate_number='KCA-456B',
            model='Isuzu Truck',
            capacity_kg=1000.0,
            status='IN_MAINTENANCE'
        )
        
        url = reverse('orders:list_vehicles')
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_assign_driver_to_vehicle_success(self):
        """Test successful driver assignment to vehicle."""
        # Create a vehicle
        vehicle = Vehicle.objects.create(
            plate_number='KCA-123A',
            model='Toyota Hiace',
            capacity_kg=750.0,
            status='ACTIVE'
        )
        
        url = reverse('orders:assign_driver_to_vehicle')
        data = {
            'vehicle_id': vehicle.id,
            'driver_id': self.driver.id
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('vehicle', response.data)
        
        # Verify driver assigned
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.driver, self.driver)
    
    def test_unassign_driver_from_vehicle(self):
        """Test unassigning driver from vehicle."""
        # Create a vehicle with assigned driver
        vehicle = Vehicle.objects.create(
            plate_number='KCA-123A',
            model='Toyota Hiace',
            capacity_kg=750.0,
            status='ACTIVE',
            driver=self.driver
        )
        
        url = reverse('orders:assign_driver_to_vehicle')
        data = {
            'vehicle_id': vehicle.id,
            'driver_id': None  # Unassign driver
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify driver unassigned
        vehicle.refresh_from_db()
        self.assertIsNone(vehicle.driver)
    
    def test_assign_driver_permission_denied(self):
        """Test driver assignment permission denied for customers."""
        vehicle = Vehicle.objects.create(
            plate_number='KCA-123A',
            model='Toyota Hiace',
            capacity_kg=750.0,
            status='ACTIVE'
        )
        
        url = reverse('orders:assign_driver_to_vehicle')
        data = {
            'vehicle_id': vehicle.id,
            'driver_id': self.driver.id
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CylinderAPITestCase(APITestCase):
    """Test cases for Cylinder management API endpoints."""
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123',
            role='CUSTOMER'
        )
        self.driver = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            role='DRIVER'
        )
        self.dispatcher = User.objects.create_user(
            username='testdispatcher',
            email='dispatcher@test.com',
            password='testpass123',
            role='DISPATCHER'
        )
        
        # Generate JWT tokens
        self.customer_tokens = JWTService.generate_token_pair(self.customer)
        self.driver_tokens = JWTService.generate_token_pair(self.driver)
        self.dispatcher_tokens = JWTService.generate_token_pair(self.dispatcher)
    
    def get_auth_header(self, tokens):
        """Helper method to get authorization header."""
        return f"Bearer {tokens['access_token']}"
    
    def test_register_cylinder_success(self):
        """Test successful cylinder registration by dispatcher."""
        url = reverse('orders:register_cylinder')
        data = {
            'serial_number': 'CYL-2024-001',
            'cylinder_type': '13KG',
            'capacity_kg': 13.0,
            'manufacturer': 'Test Gas Co.',
            'manufacturing_date': '2024-01-01',
            'expiry_date': '2039-01-01'
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('cylinder', response.data)
        self.assertIn('security', response.data)
        self.assertIn('qr_code', response.data['security'])
        self.assertIn('rfid_tag', response.data['security'])
        self.assertIn('auth_token', response.data['security'])
        self.assertEqual(response.data['cylinder']['serial_number'], 'CYL-2024-001')
    
    def test_register_cylinder_permission_denied(self):
        """Test cylinder registration permission denied for customers."""
        url = reverse('orders:register_cylinder')
        data = {
            'serial_number': 'CYL-2024-002',
            'cylinder_type': '13KG',
            'capacity_kg': 13.0,
            'manufacturer': 'Test Gas Co.',
            'manufacturing_date': '2024-01-01',
            'expiry_date': '2039-01-01'
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_scan_cylinder_qr_success(self):
        """Test successful QR code scan."""
        from .models import Cylinder
        
        # Create a cylinder
        cylinder = Cylinder.objects.create(
            serial_number='CYL-SCAN-001',
            cylinder_type='13KG',
            capacity_kg=13.0,
            manufacturer='Test Gas Co.',
            manufacturing_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365*15)).date()
        )
        
        url = reverse('orders:scan_cylinder')
        data = {
            'code': cylinder.qr_code,
            'scan_type': 'QR',
            'location_lat': -1.2921,
            'location_lng': 36.8219,
            'location_address': '123 Test Street, Nairobi'
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['verified'])
        self.assertEqual(response.data['scan_result'], 'SUCCESS')
        self.assertIn('cylinder', response.data)
        self.assertIn('security', response.data)
        self.assertEqual(response.data['cylinder']['serial_number'], 'CYL-SCAN-001')
    
    def test_scan_cylinder_invalid_code(self):
        """Test scan with invalid code."""
        url = reverse('orders:scan_cylinder')
        data = {
            'code': 'INVALID-CODE-123',
            'scan_type': 'QR'
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['verified'])
        self.assertEqual(response.data['scan_result'], 'FAILED')
    
    def test_scan_cylinder_tampered(self):
        """Test scan of tampered cylinder."""
        from .models import Cylinder
        
        # Create a tampered cylinder
        cylinder = Cylinder.objects.create(
            serial_number='CYL-TAMPER-001',
            cylinder_type='13KG',
            capacity_kg=13.0,
            manufacturer='Test Gas Co.',
            manufacturing_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365*15)).date(),
            is_tampered=True,
            tamper_notes='Seal broken'
        )
        
        url = reverse('orders:scan_cylinder')
        data = {
            'code': cylinder.qr_code,
            'scan_type': 'QR'
        }
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.dispatcher_tokens)
        )
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['verified'])
        self.assertEqual(response.data['scan_result'], 'TAMPERED')
    
    def test_get_cylinder_history(self):
        """Test getting cylinder history."""
        from .models import Cylinder, CylinderHistory
        
        # Create a cylinder
        cylinder = Cylinder.objects.create(
            serial_number='CYL-HIST-001',
            cylinder_type='13KG',
            capacity_kg=13.0,
            manufacturer='Test Gas Co.',
            manufacturing_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365*15)).date(),
            current_customer=self.customer
        )
        
        # Create some history entries
        CylinderHistory.objects.create(
            cylinder=cylinder,
            event_type='REGISTERED',
            performed_by=self.dispatcher,
            notes='Initial registration'
        )
        
        url = reverse('orders:get_cylinder_history', kwargs={'cylinder_id': cylinder.id})
        
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_auth_header(self.customer_tokens)
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
