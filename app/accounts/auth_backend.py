from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .tu_api import ThammasatAPI, create_or_update_user

class ThammasatAuthBackend(BaseBackend):
    """
    Authentication backend for Thammasat University API
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user via Thammasat API
        """
        if not username or not password:
            return None
            
        # Authenticate with Thammasat API
        tu_api = ThammasatAPI()
        user_data = tu_api.authenticate_user(username, password)
        
        if not user_data:
            return None
            
        # Create or update user based on Thammasat API data
        user = create_or_update_user(user_data)
        return user
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
