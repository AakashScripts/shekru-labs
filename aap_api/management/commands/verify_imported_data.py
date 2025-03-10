from django.core.management.base import BaseCommand
from aap_api.models import ExcelData

class Command(BaseCommand):
    help = 'Verify imported data from Excel files'

    def handle(self, *args, **options):
        records = ExcelData.objects.all()
        self.stdout.write(f'Total records: {records.count()}')
        
        # Show sample records with all fields
        self.stdout.write('\nSample Records:')
        for record in records.order_by('-created_at')[:5]:
            self.stdout.write(
                f'\nName: {record.name}'
                f'\nJob Title: {record.job_title}'
                f'\nEmail: {record.email_id}'
                f'\nPhone: {record.phone_number}'
                f'\nLocation: {record.current_location}'
                f'\nExperience: {record.total_experience}'
                f'\nCompany: {record.current_company_name}'
                f'\n-------------------'
            )