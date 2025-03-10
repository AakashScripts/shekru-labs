from import_export import resources
from .models import ExcelData

class ExcelDataResource(resources.ModelResource):
    class Meta:
        model = ExcelData
        fields = (
            'job_title',
            'date_of_application',
            'name',
            'email_id',
            'phone_number',
            'current_location',
            'total_experience',
            'current_company_name'
        )