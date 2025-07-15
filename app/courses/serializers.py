from rest_framework import serializers
from .models import Course, Enrollment, Section, Resource, Announcement, Gradebook, LogEntry

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    file_url = serializers.URLField(required=False)
    file = serializers.FileField(required=False)
    text_content = serializers.CharField(required=False, allow_blank=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    
    class Meta:
        model = Resource
        fields = ['id', 'course', 'name', 'description', 'resource_type', 'resource_type_display', 
                  'file', 'file_url', 'text_content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        resource_type = data.get('resource_type')
        file = data.get('file')
        file_url = data.get('file_url')
        text_content = data.get('text_content')
        
        # Validate based on resource_type
        if resource_type == 'file' and not file:
            raise serializers.ValidationError({'file': 'File is required for file resource type'})
        elif resource_type == 'link' and not file_url:
            raise serializers.ValidationError({'file_url': 'URL is required for link resource type'})
        elif resource_type == 'text' and not text_content:
            raise serializers.ValidationError({'text_content': 'Content is required for text resource type'})
            
        return data

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class GradebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gradebook
        fields = '__all__'

class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = '__all__'
        read_only_fields = ['timestamp']
