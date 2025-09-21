import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTService:
    """
    Senior-level JWT service for token generation, verification, and management.
    
    This service handles all JWT operations with proper error handling,
    security considerations, and logging.
    """
    
    # JWT Configuration
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_LIFETIME = timedelta(hours=24)  # 24 hours
    REFRESH_TOKEN_LIFETIME = timedelta(days=7)   # 7 days
    
    @classmethod
    def _get_secret_key(cls):
        """
        Get the secret key for JWT encoding/decoding.
        In production, this should be a strong, randomly generated key.
        """
        return getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
    
    @classmethod
    def generate_access_token(cls, user):
        """
        Generate an access token for the given user.
        
        Args:
            user: User instance
            
        Returns:
            str: JWT access token
        """
        try:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'token_type': 'access',
                'exp': datetime.utcnow() + cls.ACCESS_TOKEN_LIFETIME,
                'iat': datetime.utcnow(),
                'jti': f"access_{user.id}_{int(datetime.utcnow().timestamp())}"  # JWT ID for tracking
            }
            
            token = jwt.encode(payload, cls._get_secret_key(), algorithm=cls.ALGORITHM)
            logger.info(f"Access token generated for user: {user.email}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating access token for user {user.email}: {str(e)}")
            raise
    
    @classmethod
    def generate_refresh_token(cls, user):
        """
        Generate a refresh token for the given user.
        
        Args:
            user: User instance
            
        Returns:
            str: JWT refresh token
        """
        try:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'token_type': 'refresh',
                'exp': datetime.utcnow() + cls.REFRESH_TOKEN_LIFETIME,
                'iat': datetime.utcnow(),
                'jti': f"refresh_{user.id}_{int(datetime.utcnow().timestamp())}"
            }
            
            token = jwt.encode(payload, cls._get_secret_key(), algorithm=cls.ALGORITHM)
            logger.info(f"Refresh token generated for user: {user.email}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating refresh token for user {user.email}: {str(e)}")
            raise
    
    @classmethod
    def generate_token_pair(cls, user):
        """
        Generate both access and refresh tokens for the user.
        
        Args:
            user: User instance
            
        Returns:
            dict: Dictionary containing access and refresh tokens
        """
        return {
            'access_token': cls.generate_access_token(user),
            'refresh_token': cls.generate_refresh_token(user),
            'token_type': 'Bearer',
            'expires_in': int(cls.ACCESS_TOKEN_LIFETIME.total_seconds())
        }
    
    @classmethod
    def verify_token(cls, token, token_type='access'):
        """
        Verify and decode a JWT token.
        
        Args:
            token (str): JWT token to verify
            token_type (str): Expected token type ('access' or 'refresh')
            
        Returns:
            dict: Decoded token payload
            
        Raises:
            jwt.ExpiredSignatureError: Token has expired
            jwt.InvalidTokenError: Token is invalid
            ValueError: Token type mismatch
        """
        try:
            payload = jwt.decode(
                token, 
                cls._get_secret_key(), 
                algorithms=[cls.ALGORITHM],
                options={'require': ['exp', 'iat', 'user_id']}
            )
            
            # Verify token type
            if payload.get('token_type') != token_type:
                raise ValueError(f"Expected {token_type} token, got {payload.get('token_type')}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired {token_type} token used")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid {token_type} token: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error verifying {token_type} token: {str(e)}")
            raise
    
    @classmethod
    def get_user_from_token(cls, token, token_type='access'):
        """
        Extract and return the user from a JWT token.
        
        Args:
            token (str): JWT token
            token_type (str): Expected token type
            
        Returns:
            User: User instance or None if not found
            
        Raises:
            jwt.ExpiredSignatureError: Token has expired
            jwt.InvalidTokenError: Token is invalid
        """
        try:
            payload = cls.verify_token(token, token_type)
            user_id = payload.get('user_id')
            
            if not user_id:
                logger.warning("Token payload missing user_id")
                return None
            
            try:
                user = User.objects.get(id=user_id, is_active=True)
                return user
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found or inactive")
                return None
                
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Re-raise JWT errors for proper handling upstream
            raise
        except Exception as e:
            logger.error(f"Error extracting user from token: {str(e)}")
            return None
    
    @classmethod
    def refresh_access_token(cls, refresh_token):
        """
        Generate a new access token using a refresh token.
        
        Args:
            refresh_token (str): Valid refresh token
            
        Returns:
            dict: New token pair
            
        Raises:
            jwt.ExpiredSignatureError: Refresh token has expired
            jwt.InvalidTokenError: Refresh token is invalid
        """
        user = cls.get_user_from_token(refresh_token, token_type='refresh')
        
        if not user:
            raise jwt.InvalidTokenError("Invalid refresh token")
        
        return cls.generate_token_pair(user)
    
    @classmethod
    def is_token_expired(cls, token):
        """
        Check if a token is expired without raising an exception.
        
        Args:
            token (str): JWT token to check
            
        Returns:
            bool: True if expired, False if valid, None if invalid format
        """
        try:
            payload = jwt.decode(
                token, 
                cls._get_secret_key(), 
                algorithms=[cls.ALGORITHM],
                options={'verify_exp': False}  # Don't verify expiration
            )
            
            exp = payload.get('exp')
            if exp:
                return datetime.utcnow() > datetime.fromtimestamp(exp)
            return None
            
        except jwt.InvalidTokenError:
            return None
    
    @classmethod
    def blacklist_token(cls, token):
        """
        Add token to blacklist (for logout functionality).
        
        Note: In a production environment, you might want to store
        blacklisted tokens in Redis or a database table.
        For now, this is a placeholder for the implementation.
        
        Args:
            token (str): Token to blacklist
        """
        # TODO: Implement token blacklisting in production
        # This could be done using Redis or a database table
        logger.info(f"Token blacklisted (placeholder implementation)")
        pass