from django.db import models
import uuid
from django.contrib.auth.models import User
from courses.models import Course

class Assignment(models.Model):
    """
    Model representing an assignment
    """
    SUBMISSION_TYPES = (
        ('file', 'File Upload'),
        ('text', 'Text Entry'),
        ('link', 'URL Link'),
        ('code', 'Code'),
    )
    
    ASSIGNMENT_TYPES = (
        ('homework', 'Homework'),
        ('classwork', 'Classwork'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    assignment_type = models.CharField(max_length=10, choices=ASSIGNMENT_TYPES, default='homework')
    submission_type = models.CharField(max_length=10, choices=SUBMISSION_TYPES, default='file')
    due_date = models.DateTimeField()
    available_from = models.DateTimeField()
    total_points = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.course.code}"

class Submission(models.Model):
    """
    Model representing a student's submission for an assignment
    """
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('late', 'Late'),
        ('graded', 'Graded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    text_content = models.TextField(blank=True)
    link_url = models.URLField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    resubmission_count = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('assignment', 'student')
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.name}"
