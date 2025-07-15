from django.contrib import admin
from .models import Course, Enrollment, Section, Resource, Announcement, Gradebook, LogEntry

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Section)
admin.site.register(Resource)
admin.site.register(Announcement)
admin.site.register(Gradebook)
admin.site.register(LogEntry)
