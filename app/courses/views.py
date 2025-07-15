from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Enrollment, Section, Resource, Announcement, Gradebook, LogEntry
from .serializers import (
    CourseSerializer, EnrollmentSerializer, SectionSerializer,
    ResourceSerializer, AnnouncementSerializer, GradebookSerializer,
    LogEntrySerializer
)
from .permissions import IsTeacherOrReadOnly, IsEnrolledOrTeacher, IsOwnerOrTeacher

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'term', 'year', 'department', 'faculty']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'year', 'term', 'created_at']

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrTeacher]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student_tu_id', 'course', 'status']
    
    def get_queryset(self):
        user_id = str(self.request.user.id)
        # If user is a teacher, show enrollments for their courses
        teacher_courses = Course.objects.filter(teachers__contains=[user_id])
        if teacher_courses.exists():
            return Enrollment.objects.filter(course__in=teacher_courses)
        # Otherwise, show only user's enrollments
        return Enrollment.objects.filter(student_tu_id=user_id)

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        user_id = str(self.request.user.id)
        # If user is a teacher, show all sections for their courses
        teacher_courses = Course.objects.filter(teachers__contains=[user_id])
        if teacher_courses.exists():
            return Section.objects.filter(course__in=teacher_courses)
        # Otherwise, show sections for courses user is enrolled in
        enrolled_courses = Course.objects.filter(enrollment__student_tu_id=user_id, enrollment__status='enrolled')
        return Section.objects.filter(course__in=enrolled_courses)

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course', 'resource_type']
    search_fields = ['name', 'description']
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        user_id = str(self.request.user.id)
        # If user is a teacher, show all resources for their courses
        teacher_courses = Course.objects.filter(teachers__contains=[user_id])
        if teacher_courses.exists():
            return Resource.objects.filter(course__in=teacher_courses)
        # Otherwise, show resources for courses user is enrolled in
        enrolled_courses = Course.objects.filter(enrollment__student_tu_id=user_id, enrollment__status='enrolled')
        return Resource.objects.filter(course__in=enrolled_courses)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course']
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        user_id = str(self.request.user.id)
        # If user is a teacher, show all announcements for their courses
        teacher_courses = Course.objects.filter(teachers__contains=[user_id])
        if teacher_courses.exists():
            return Announcement.objects.filter(course__in=teacher_courses)
        # Otherwise, show announcements for courses user is enrolled in
        enrolled_courses = Course.objects.filter(enrollment__student_tu_id=user_id, enrollment__status='enrolled')
        return Announcement.objects.filter(course__in=enrolled_courses)

class GradebookViewSet(viewsets.ModelViewSet):
    queryset = Gradebook.objects.all()
    serializer_class = GradebookSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']
    
    def get_queryset(self):
        user_id = str(self.request.user.id)
        # If user is a teacher, show all gradebooks for their courses
        teacher_courses = Course.objects.filter(teachers__contains=[user_id])
        if teacher_courses.exists():
            return Gradebook.objects.filter(course__in=teacher_courses)
        # Otherwise, show gradebooks for courses user is enrolled in
        enrolled_courses = Course.objects.filter(enrollment__student_tu_id=user_id, enrollment__status='enrolled')
        return Gradebook.objects.filter(course__in=enrolled_courses)

class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing log entries.
    This is read-only to ensure logs cannot be modified.
    """
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tu_user_id', 'action', 'is_abnormal']
    search_fields = ['action', 'message']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']  # Default to newest first
    
    def get_queryset(self):
        user_id = str(self.request.user.id)
        # Only teachers or admins should see all logs
        # For now, we'll just limit to the user's own logs
        return LogEntry.objects.filter(tu_user_id=user_id)
