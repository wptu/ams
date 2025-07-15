import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class TUAPIClient:
    """
    Client for interacting with the Thammasat University API
    """
    def __init__(self):
        self.base_url = settings.TU_API_URL
        self.api_key = settings.TU_API_KEY
        self.timeout = getattr(settings, 'TU_API_TIMEOUT', 10)  # Default 10 seconds
        self.cache_timeout = getattr(settings, 'TU_API_CACHE_TIMEOUT', 3600)  # Default 1 hour
    
    def _get_headers(self):
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method, endpoint, params=None, data=None, cache_key=None):
        """
        Make a request to the TU API with caching support
        """
        # Check cache first if cache_key is provided
        if cache_key:
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
        
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Cache the result if cache_key is provided
            if cache_key:
                cache.set(cache_key, result, self.cache_timeout)
            
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"TU API request failed: {str(e)}")
            return None
    
    def verify_token(self, token):
        """
        Verify a user's authentication token
        """
        return self._make_request(
            method='POST',
            endpoint='auth/verify',
            data={'token': token}
        )
    
    def get_user_info(self, user_id):
        """
        Get information about a user by their TU ID
        """
        cache_key = f"tu_api_user_{user_id}"
        return self._make_request(
            method='GET',
            endpoint=f'users/{user_id}',
            cache_key=cache_key
        )
    
    def get_user_courses(self, user_id):
        """
        Get courses associated with a user (either as teacher or student)
        """
        cache_key = f"tu_api_user_courses_{user_id}"
        return self._make_request(
            method='GET',
            endpoint=f'users/{user_id}/courses',
            cache_key=cache_key
        )
    
    def authenticate(self, username, password):
        """
        Authenticate a user with username and password
        """
        return self._make_request(
            method='POST',
            endpoint='auth/login',
            data={
                'username': username,
                'password': password
            }
        )

# Create a singleton instance
tu_api_client = TUAPIClient()
