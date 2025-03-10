from django.core.management.base import BaseCommand
from aap_api.models import ExcelData
from django.db.models import Q

class Command(BaseCommand):
    help = 'Delete records with null or empty values in critical fields'

    def handle(self, *args, **kwargs):
        initial_count = ExcelData.objects.count()
        
        deleted = ExcelData.objects.filter(
            Q(name__isnull=True) | Q(name='') |
            Q(job_title__isnull=True) | Q(job_title='') |
            Q(email_id__isnull=True) | Q(email_id='') |
            Q(phone_number__isnull=True) | Q(phone_number='') |
            Q(current_location__isnull=True) | Q(current_location='') |
            Q(total_experience__isnull=True) | Q(total_experience='')
        ).delete()

        final_count = ExcelData.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {initial_count - final_count} null records. '
                f'Remaining records: {final_count}'
            )
        )