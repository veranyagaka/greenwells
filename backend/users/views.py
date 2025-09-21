from django.contrib.auth import login, logout
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

# Set up logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    User registration endpoint.
    
    Allows new users to create an account with email, username, password, and other details.
    """
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Log successful registration
            logger.info(f"New user registered: {user.email}")
            
            # Return user info without password
            user_serializer = UserInfoSerializer(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': user_serializer.data
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
    
    Authenticates users with email and password, creates a session.
    """
    try:
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create session
            login(request, user)
            
            # Log successful login
            logger.info(f"User logged in: {user.email}")
            
            # Return user info
            user_serializer = UserInfoSerializer(user)
            
            return Response({
                'message': 'Login successful',
                'user': user_serializer.data
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
    
    Logs out the authenticated user and destroys the session.
    """
    try:
        user_email = request.user.email
        
        # Destroy session
        logout(request)
        
        # Log successful logout
        logger.info(f"User logged out: {user_email}")
        
        return Response({
            'message': 'Logout successful'
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
