from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, EnrollmentViewSet, SectionViewSet,
    ResourceViewSet, AnnouncementViewSet, GradebookViewSet,
    LogEntryViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'resources', ResourceViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'gradebooks', GradebookViewSet)
router.register(r'logs', LogEntryViewSet)

urlpatterns = router.urls
