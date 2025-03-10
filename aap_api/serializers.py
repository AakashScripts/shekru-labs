from rest_framework import serializers
from .models import ExcelData

class ExcelDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelData
        fields = [
            'id', 
            'name', 
            'job_title', 
            'email_id', 
            'phone_number',
            'current_location', 
            'total_experience', 
            'current_company_name'
        ]
        
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=2*1024*1024*1024) # 2GB