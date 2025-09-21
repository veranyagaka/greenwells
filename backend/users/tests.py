from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
import json
import jwt

from .jwt_service import JWTService

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


class JWTServiceTests(TestCase):
    """Test cases for JWT service functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            role='CUSTOMER'
        )
    
    def test_generate_access_token(self):
        """Test generating access token."""
        token = JWTService.generate_access_token(self.user)
        self.assertIsNotNone(token)
        
        # Verify token contains user data
        payload = JWTService.verify_token(token, 'access')
        self.assertEqual(payload['user_id'], self.user.id)
        self.assertEqual(payload['email'], self.user.email)
        self.assertEqual(payload['token_type'], 'access')
    
    def test_generate_refresh_token(self):
        """Test generating refresh token."""
        token = JWTService.generate_refresh_token(self.user)
        self.assertIsNotNone(token)
        
        # Verify token contains user data
        payload = JWTService.verify_token(token, 'refresh')
        self.assertEqual(payload['user_id'], self.user.id)
        self.assertEqual(payload['token_type'], 'refresh')
    
    def test_generate_token_pair(self):
        """Test generating token pair."""
        tokens = JWTService.generate_token_pair(self.user)
        
        self.assertIn('access_token', tokens)
        self.assertIn('refresh_token', tokens)
        self.assertIn('token_type', tokens)
        self.assertIn('expires_in', tokens)
        self.assertEqual(tokens['token_type'], 'Bearer')
    
    def test_verify_token_invalid_type(self):
        """Test verifying token with wrong type."""
        access_token = JWTService.generate_access_token(self.user)
        
        with self.assertRaises(ValueError):
            JWTService.verify_token(access_token, 'refresh')
    
    def test_get_user_from_token(self):
        """Test extracting user from token."""
        token = JWTService.generate_access_token(self.user)
        extracted_user = JWTService.get_user_from_token(token)
        
        self.assertEqual(extracted_user.id, self.user.id)
        self.assertEqual(extracted_user.email, self.user.email)
    
    def test_refresh_access_token(self):
        """Test refreshing access token."""
        refresh_token = JWTService.generate_refresh_token(self.user)
        new_tokens = JWTService.refresh_access_token(refresh_token)
        
        self.assertIn('access_token', new_tokens)
        self.assertIn('refresh_token', new_tokens)
        
        # Verify new access token works
        user = JWTService.get_user_from_token(new_tokens['access_token'])
        self.assertEqual(user.id, self.user.id)


class AuthenticationAPITests(APITestCase):
    """Test cases for JWT authentication API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.signup_url = reverse('users:signup')
        self.login_url = reverse('users:login')
        self.signout_url = reverse('users:signout')
        self.userinfo_url = reverse('users:userinfo')
        self.refresh_url = reverse('users:refresh_token')
        self.verify_url = reverse('users:verify_token')
        
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'CUSTOMER',
            'phone_number': '+1234567890',
            'address': '123 Test Street'
        }
    
    def test_signup_returns_jwt_tokens(self):
        """Test signup returns JWT tokens."""
        response = self.client.post(
            self.signup_url,
            self.valid_user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        
        tokens = response.data['tokens']
        self.assertIn('access_token', tokens)
        self.assertIn('refresh_token', tokens)
        self.assertEqual(tokens['token_type'], 'Bearer')
    
    def test_login_returns_jwt_tokens(self):
        """Test login returns JWT tokens."""
        # Create a user first
        User.objects.create_user(
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
        self.assertIn('tokens', response.data)
        
        tokens = response.data['tokens']
        self.assertIn('access_token', tokens)
        self.assertIn('refresh_token', tokens)
    
    def test_userinfo_with_jwt_token(self):
        """Test accessing user info with JWT token."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            role='DRIVER'
        )
        
        token = JWTService.generate_access_token(user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.userinfo_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_userinfo_without_token(self):
        """Test accessing user info without token."""
        response = self.client.get(self.userinfo_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_userinfo_with_invalid_token(self):
        """Test accessing user info with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(self.userinfo_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token_endpoint(self):
        """Test token refresh endpoint."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        refresh_token = JWTService.generate_refresh_token(user)
        
        response = self.client.post(
            self.refresh_url,
            {'refresh_token': refresh_token},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
    
    def test_verify_token_endpoint(self):
        """Test token verification endpoint."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        token = JWTService.generate_access_token(user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.verify_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertIn('user', response.data)
    
    def test_signout_with_jwt(self):
        """Test signing out with JWT token."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        token = JWTService.generate_access_token(user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.signout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
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