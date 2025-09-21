from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Custom session authentication that exempts CSRF for API endpoints.
    This is acceptable for API endpoints when proper authorization is in place.
    """
    
    def enforce_csrf(self, request):
        """
        Override to skip CSRF check for API endpoints.
        """
        return  # Skip CSRF check