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
        self.assertEqual(str(self.vehicle), "TEST-123 - Toyota Hiace")
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
