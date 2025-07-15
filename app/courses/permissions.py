from rest_framework import permissions

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers of a course to edit it.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Check if user is a teacher of this course
        if hasattr(obj, 'teachers'):
            # Direct course object
            return str(request.user.id) in obj.teachers
        elif hasattr(obj, 'course'):
            # Related object (Section, Resource, Announcement, etc.)
            return str(request.user.id) in obj.course.teachers
        
        # Default deny if we can't determine
        return False

class IsEnrolledOrTeacher(permissions.BasePermission):
    """
    Permission to only allow students enrolled in a course or teachers to view it.
    """
    def has_permission(self, request, view):
        # All authenticated users can list courses
        if request.method == 'GET' and 'pk' not in view.kwargs:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user_id = str(request.user.id)
        
        # Teachers can do anything
        if hasattr(obj, 'teachers') and user_id in obj.teachers:
            return True
        elif hasattr(obj, 'course') and user_id in obj.course.teachers:
            return True
        
        # For enrollment objects
        if hasattr(obj, 'student_tu_id') and obj.student_tu_id == user_id:
            return True
        
        # Check if user is enrolled in this course
        if hasattr(obj, 'course'):
            # Check through enrollments
            return obj.course.enrollment_set.filter(student_tu_id=user_id, status='enrolled').exists()
        
        # For course objects
        if hasattr(obj, 'enrollment_set'):
            # Check if user is enrolled
            return obj.enrollment_set.filter(student_tu_id=user_id, status='enrolled').exists()
        
        return False

class IsOwnerOrTeacher(permissions.BasePermission):
    """
    Permission to only allow owners of a resource or teachers to edit it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user_id = str(request.user.id)
        
        # Teachers can do anything
        if hasattr(obj, 'course') and user_id in obj.course.teachers:
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'student_tu_id') and obj.student_tu_id == user_id:
            return True
            
        return False
