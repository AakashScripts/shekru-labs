from django.core.management.base import BaseCommand
from aap_api.models import ExcelData
from django.db import transaction

class Command(BaseCommand):
    help = 'Delete records with empty fields'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                deleted_count = ExcelData.objects.filter(
                    name='',
                    job_title='',
                    email_id='',
                    phone_number='',
                    current_location='',
                    total_experience='',
                    current_company_name=''
                ).delete()[0]
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {deleted_count} empty records')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error deleting records: {str(e)}')
            )