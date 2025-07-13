from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extension of the User model to store additional information about users
    """
    USER_TYPES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    tu_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True)
    faculty = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
