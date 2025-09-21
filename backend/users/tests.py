from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
import json

User = get_user_model()


class UserModelTests(TestCase):
    """Test cases for the User model."""
    
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        username = 'testuser'
        
        user = User.objects.create_user(
            email=email,
            password=password,
            username=username
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.username, username)
        self.assertEqual(user.role, 'CUSTOMER')  # Default role
    
    def test_new_user_email_normalized(self):
        """Test that email for a new user is normalized."""
        email = 'test@EXAMPLE.COM'
        user = User.objects.create_user(
            email=email,
            password='testpass123',
            username='testuser'
        )
        
        self.assertEqual(user.email, email.lower())
    
    def test_new_user_without_email_raises_error(self):
        """Test creating user without email raises ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(None, 'testpass123')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            'admin@example.com',
            'testpass123',
            username='admin'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.role, 'ADMIN')


class AuthenticationAPITests(APITestCase):
    """Test cases for authentication API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.signup_url = reverse('users:signup')
        self.login_url = reverse('users:login')
        self.signout_url = reverse('users:signout')
        self.userinfo_url = reverse('users:userinfo')
        
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'CUSTOMER',
            'phone_number': '+1234567890',
            'address': '123 Test Street'
        }
    
    def test_signup_valid_user(self):
        """Test signing up with valid user data."""
        response = self.client.post(
            self.signup_url,
            self.valid_user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        
        # Verify user was created in database
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
    
    def test_signup_password_mismatch(self):
        """Test signup fails when passwords don't match."""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password_confirm'] = 'differentpassword'
        
        response = self.client.post(
            self.signup_url,
            invalid_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_signup_duplicate_email(self):
        """Test signup fails with duplicate email."""
        # Create first user
        User.objects.create_user(
            email='test@example.com',
            username='firstuser',
            password='testpass123'
        )
        
        response = self.client.post(
            self.signup_url,
            self.valid_user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_valid_credentials(self):
        """Test login with valid credentials."""
        # Create a user
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_userinfo_authenticated(self):
        """Test getting user info when authenticated."""
        # Create and login a user
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            role='DRIVER',
            phone_number='+1234567890'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.userinfo_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['role'], 'DRIVER')
    
    def test_userinfo_unauthenticated(self):
        """Test getting user info when not authenticated."""
        response = self.client.get(self.userinfo_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_signout_authenticated(self):
        """Test signing out when authenticated."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.signout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_signout_unauthenticated(self):
        """Test signing out when not authenticated."""
        response = self.client.post(self.signout_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
