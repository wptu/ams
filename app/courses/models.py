from django.db import models
import uuid
from django.contrib.auth.models import User

class Course(models.Model):
    """
    Model representing a course/class
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    term = models.CharField(max_length=20)  # e.g., "2023/1"
    year = models.IntegerField()
    teachers = models.ManyToManyField(User, related_name='teaching_courses')
    students = models.ManyToManyField(User, related_name='enrolled_courses', through='Enrollment')
    department = models.CharField(max_length=100, blank=True)
    faculty = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.term})"

class Enrollment(models.Model):
    """
    Model representing a student's enrollment in a course
    """
    STATUS_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('withdrawn', 'Withdrawn'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='enrolled')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.username} - {self.course.code} - {self.status}"
