from django.core.management.base import BaseCommand
from aap_api.models import ExcelData

class Command(BaseCommand):
    help = 'Verify imported Excel data'

    def handle(self, *args, **kwargs):
        total = ExcelData.objects.count()
        with_data = ExcelData.objects.exclude(
            name='',
            job_title='',
            email_id='',
            phone_number='',
            current_location='',
            total_experience='',
            current_company_name=''
        ).count()

        self.stdout.write(self.style.SUCCESS(f'Total records: {total}'))
        self.stdout.write(self.style.SUCCESS(f'Records with data: {with_data}'))
        
        # Show sample records
        self.stdout.write('\nSample Records:')
        for record in ExcelData.objects.exclude(name='')[:5]:
            self.stdout.write(
                f'\nName: {record.name}\n'
                f'Job: {record.job_title}\n'
                f'Email: {record.email_id}\n'
                f'Location: {record.current_location}\n'
                f'-------------------'
            )