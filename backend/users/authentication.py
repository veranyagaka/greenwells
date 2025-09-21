import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .jwt_service import JWTService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for Django REST Framework.
    
    This authentication class handles JWT token verification and user extraction
    for all protected endpoints. It follows Django REST Framework best practices
    and provides comprehensive error handling.
    """
    
    authentication_header_prefix = 'Bearer'
    
    def authenticate(self, request):
        """
        Authenticate the request using JWT token from Authorization header.
        
        Args:
            request: Django request object
            
        Returns:
            tuple: (user, token) if authentication successful, None otherwise
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        auth_header = self.get_authorization_header(request)
        
        if not auth_header:
            return None
        
        try:
            token = self.extract_token(auth_header)
            if not token:
                return None
            
            user = self.authenticate_credentials(token)
            return (user, token)
            
        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            raise AuthenticationFailed('Authentication failed due to server error')
    
    def get_authorization_header(self, request):
        """
        Extract the authorization header from the request.
        
        Args:
            request: Django request object
            
        Returns:
            str: Authorization header value or None
        """
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            return None
        
        return auth.strip()
    
    def extract_token(self, auth_header):
        """
        Extract JWT token from authorization header.
        
        Args:
            auth_header (str): Authorization header value
            
        Returns:
            str: JWT token or None
            
        Raises:
            AuthenticationFailed: If header format is invalid
        """
        auth_parts = auth_header.split()
        
        if len(auth_parts) != 2:
            raise AuthenticationFailed('Invalid authorization header format')
        
        auth_type, token = auth_parts
        
        if auth_type.lower() != self.authentication_header_prefix.lower():
            return None  # Not a Bearer token, let other authenticators try
        
        if not token:
            raise AuthenticationFailed('No token provided')
        
        return token
    
    def authenticate_credentials(self, token):
        """
        Authenticate the user using the JWT token.
        
        Args:
            token (str): JWT token
            
        Returns:
            User: Authenticated user instance
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        try:
            user = JWTService.get_user_from_token(token, token_type='access')
            
            if not user:
                raise AuthenticationFailed('Invalid token: user not found')
            
            if not user.is_active:
                raise AuthenticationFailed('User account is disabled')
            
            return user
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            logger.error(f"Token authentication error: {str(e)}")
            raise AuthenticationFailed('Authentication failed')
    
    def authenticate_header(self, request):
        """
        Return the authentication header for 401 responses.
        
        This tells the client what authentication method is expected.
        
        Returns:
            str: Authentication header string
        """
        return self.authentication_header_prefix


class CsrfExemptSessionAuthentication:
    """
    Deprecated: Keeping for backward compatibility but not used with JWT.
    JWT authentication doesn't require CSRF protection as tokens are stateless.
    """
    pass