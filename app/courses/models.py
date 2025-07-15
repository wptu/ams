from django.db import models
import uuid

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
    teachers = models.JSONField(default=list)   # list of TU user_id
    tas = models.JSONField(default=list, blank=True) # list of TU user_id
    department = models.CharField(max_length=100, blank=True)
    faculty = models.CharField(max_length=100, blank=True)
    sections = models.CharField(max_length=50, blank=True)
    settings = models.JSONField(default=dict, blank=True)  # for course policies
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
    student_tu_id = models.CharField(max_length=20)  # TU student_id
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='enrolled')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student_tu_id', 'course')

    def __str__(self):
        return f"{self.student_tu_id} - {self.course.code} - {self.status}"

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

class Resource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=255)
    file_url = models.URLField(blank=True)
    description = models.TextField(blank=True)

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Gradebook(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='gradebook')
    data = models.JSONField(default=dict, blank=True)

class LogEntry(models.Model):
    tu_user_id = models.CharField(max_length=20, blank=True, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    is_abnormal = models.BooleanField(default=False)
