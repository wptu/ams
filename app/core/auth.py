from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from .tu_api import tu_api_client
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class TUAPIBackend(BaseBackend):
    """
    Authentication backend that uses the TU API
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user via TU API
        """
        # Skip this backend if TU API is not configured
        if not hasattr(settings, 'TU_API_BASE_URL') or not hasattr(settings, 'TU_API_KEY'):
            return None
        
        # Try to authenticate with TU API
        auth_response = tu_api_client.authenticate(username, password)
        
        if not auth_response or 'user_id' not in auth_response:
            logger.warning(f"TU API authentication failed for user: {username}")
            return None
        
        user_id = auth_response['user_id']
        token = auth_response.get('token')
        
        # Get or create the user in our database
        try:
            user = User.objects.get(username=user_id)
            # Update user info if needed
            if token:
                user.tu_api_token = token
                user.save(update_fields=['tu_api_token'])
        except User.DoesNotExist:
            # Create a new user
            user_info = tu_api_client.get_user_info(user_id)
            if not user_info:
                logger.error(f"Failed to get user info from TU API for user_id: {user_id}")
                return None
            
            # Create the user with information from TU API
            user = User.objects.create(
                username=user_id,
                email=user_info.get('email', ''),
                first_name=user_info.get('first_name', ''),
                last_name=user_info.get('last_name', ''),
                tu_api_token=token
            )
        
        return user
    
    def get_user(self, user_id):
        """
        Get a user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
