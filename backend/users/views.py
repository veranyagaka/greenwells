import jwt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import logging

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserInfoSerializer
)
from .jwt_service import JWTService

# Set up logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    User registration endpoint.
    
    Creates a new user account and returns JWT tokens for immediate authentication.
    """
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Log successful registration
            logger.info(f"New user registered: {user.email}")
            
            # Generate JWT token pair for immediate authentication
            tokens = JWTService.generate_token_pair(user)
            
            # Return user info and tokens
            user_serializer = UserInfoSerializer(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': user_serializer.data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Registration failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response({
            'error': 'Internal server error during registration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint.
    
    Authenticates users with email and password, returns JWT tokens.
    """
    try:
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT token pair
            tokens = JWTService.generate_token_pair(user)
            
            # Log successful login
            logger.info(f"User logged in: {user.email}")
            
            # Return user info and tokens
            user_serializer = UserInfoSerializer(user)
            
            return Response({
                'message': 'Login successful',
                'user': user_serializer.data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Login failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({
            'error': 'Internal server error during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout_view(request):
    """
    User logout endpoint.
    
    Invalidates the current JWT token (token blacklisting).
    Note: In a stateless JWT system, true logout requires token blacklisting
    or client-side token deletion.
    """
    try:
        user_email = request.user.email
        
        # Extract token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Add token to blacklist (implementation depends on your blacklist strategy)
            JWTService.blacklist_token(token)
        
        # Log successful logout
        logger.info(f"User logged out: {user_email}")
        
        return Response({
            'message': 'Logout successful',
            'detail': 'Token has been invalidated. Please remove it from client storage.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'error': 'Internal server error during logout'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userinfo_view(request):
    """
    User information endpoint.
    
    Returns the authenticated user's information.
    JWT token is verified by the authentication middleware.
    """
    try:
        user_serializer = UserInfoSerializer(request.user)
        
        return Response({
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"User info error: {str(e)}")
        return Response({
            'error': 'Internal server error while fetching user info'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Token refresh endpoint.
    
    Accepts a refresh token and returns a new access token.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate new token pair using refresh token
            tokens = JWTService.refresh_access_token(refresh_token)
            
            return Response({
                'message': 'Token refreshed successfully',
                'tokens': tokens
            }, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({
                'error': 'Refresh token has expired',
                'detail': 'Please log in again'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        except jwt.InvalidTokenError:
            return Response({
                'error': 'Invalid refresh token',
                'detail': 'Please log in again'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return Response({
            'error': 'Internal server error during token refresh'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_token_view(request):
    """
    Token verification endpoint.
    
    Verifies if the current token is valid and returns user information.
    Useful for client-side token validation.
    """
    try:
        # If we reach here, the token is valid (verified by authentication middleware)
        user_serializer = UserInfoSerializer(request.user)
        
        return Response({
            'valid': True,
            'user': user_serializer.data,
            'message': 'Token is valid'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return Response({
            'error': 'Internal server error during token verification'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
