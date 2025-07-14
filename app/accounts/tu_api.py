import os
import json
import logging
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile

# Set up logger
logger = logging.getLogger(__name__)

class ThammasatAPI:
    """
    Class for interacting with Thammasat University REST API
    """
    def __init__(self):
        """
        Initialize the API client with API URL and key from settings
        """
        self.api_url = getattr(settings, 'TU_API_URL', 'https://restapi.tu.ac.th/api/v1/auth/Ad/verify')
        self.api_key = getattr(settings, 'TU_API_KEY', 'your-api-key')
        self.profile_api_url = 'https://restapi.tu.ac.th/api/v2/profile/std/info/'
        
        # Set up headers with API key - using the full API key provided
        # TU65a87311d303b5bd29ce61c0ab7a79dff942fa2d9728a86c80a02a17e38718303a18cd84f87bbc52068e9d8a6e721054
        self.headers = {
            'Application-Key': self.api_key,  # Changed from Authorization to Application-Key
            'Content-Type': 'application/json'
        }
        
        # Log the API configuration
        logger.info(f"Initialized Thammasat API client with URL: {self.api_url}")
        logger.debug(f"API Key length: {len(self.api_key) if self.api_key else 'None'}")
        logger.debug(f"Headers: {self.headers}")
        
        # Warn if API key doesn't start with TU prefix
        if not self.api_key.startswith('TU'):
            logger.warning("API Key does not start with 'TU' prefix, which may be required by Thammasat API")
            
    def get_student_info(self, student_id):
        """
        Get student profile information from Thammasat API v2
        
        Args:
            student_id (str): Student ID (e.g., 60123XXXXXX)
            
        Returns:
            dict: Student profile data if successful, None otherwise
        """
        try:
            # Construct the URL with query parameter
            endpoint = f"{self.profile_api_url}?id={student_id}"
            logger.info(f"Getting student info for ID {student_id} from {endpoint}")
            
            # Make the API request
            logger.debug(f"Sending GET request to {endpoint}")
            response = requests.get(endpoint, headers=self.headers)
            
            # Log response details
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved student info for ID {student_id}")
                return data
            else:
                logger.warning(f"Failed to get student info for ID {student_id}. Status code: {response.status_code}")
                if response.content:
                    try:
                        error_data = response.json()
                        logger.warning(f"Error response: {error_data}")
                    except json.JSONDecodeError:
                        logger.warning(f"Non-JSON error response: {response.content}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting student info: {str(e)}")
            return None
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user with Thammasat API
        Returns user data if authentication is successful, None otherwise
        """
        try:
            # Debug API configuration
            logger.debug(f"TU_API_URL: {settings.TU_API_URL}")
            logger.debug(f"API Key length: {len(settings.TU_API_KEY) if settings.TU_API_KEY else 'None'}")
            
            # Use the API URL directly without appending /auth
            endpoint = self.api_url
            logger.info(f"Authenticating user {username} with Thammasat API at {endpoint}")
            
            payload = {
                'UserName': username,
                'PassWord': password
            }
            
            # Debug request headers (without showing full API key)
            safe_headers = self.headers.copy()
            if 'Authorization' in safe_headers:
                auth_value = safe_headers['Authorization']
                if auth_value.startswith('Bearer '):
                    safe_headers['Authorization'] = f"Bearer {auth_value[7:15]}..." # Show only part of the token
            logger.debug(f"Request headers: {safe_headers}")
            
            # Make the API request with timeout to prevent worker hanging
            logger.debug(f"Sending POST request to {endpoint}")
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=10)
            
            # Log response details
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                logger.info(f"Authentication successful for user {username}")
                return response.json()
            else:
                logger.warning(f"Authentication failed for user {username}. Status code: {response.status_code}")
                try:
                    error_content = response.json()
                    logger.warning(f"Error response: {error_content}")
                except:
                    logger.warning(f"Error response content: {response.text[:500]}")
                return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return None
    
    def get_user_role(self, user_data):
        # Logic to determine role based on TU API response
        # This would depend on the actual structure of TU API response
        
        # Check user type from the response
        if 'type' in user_data:
            user_type = user_data['type'].lower()
            if user_type == 'employee':
                # For employees, check department/organization to determine if admin or teacher
                department = user_data.get('department', '').lower()
                organization = user_data.get('organization', '').lower()
                
                # Admin roles typically in IT/admin departments
                if 'เทคโนโลยีสารสนเทศ' in organization or 'it' in department or 'admin' in department:
                    return 'admin'
                else:
                    return 'teacher'
            elif user_type == 'student':
                return 'student'
        
        # Default role if type not specified or recognized
        return 'student'

def create_or_update_user(tu_user_data):
    """
    Create or update Django User and UserProfile based on Thammasat API data
    """
    if not tu_user_data:
        raise ValidationError("Invalid user data from Thammasat API")
    
    # Extract basic user information from the authentication response
    username = tu_user_data.get('username')
    if not username:
        raise ValidationError("Username is required")
        
    # Use username as tu_id if not provided in the API response
    tu_id = tu_user_data.get('tu_id', username)
    
    # Extract other user information from the authentication response
    email = tu_user_data.get('email', '')
    
    # Extract name from displayname fields if available
    display_name_th = tu_user_data.get('displayname_th', '')
    display_name_en = tu_user_data.get('displayname_en', '')
    
    # Use Thai name if available, otherwise use English name
    if display_name_th:
        # Try to split Thai name into first and last name
        name_parts = display_name_th.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
    elif display_name_en:
        # Try to split English name into first and last name
        name_parts = display_name_en.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
    else:
        # Fallback if no name is available
        first_name = ''
        last_name = ''
    
    # Get or create Django User
    try:
        user = User.objects.get(username=username)
        # Update existing user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    except User.DoesNotExist:
        # Create new user with unusable password (auth is via TU API)
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_unusable_password()
        user.save()
    
    # Get or create UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
    
    # Update profile with TU data
    profile.tu_id = tu_id
    profile.faculty = tu_user_data.get('faculty', '')
    profile.department = tu_user_data.get('department', '')
    
    # Determine role
    tu_api = ThammasatAPI()
    role = tu_api.get_user_role(tu_user_data)
    if role:
        profile.user_type = role
    
    profile.save()
    
    return user
