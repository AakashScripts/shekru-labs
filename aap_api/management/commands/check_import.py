from django.core.management.base import BaseCommand
from aap_api.models import ExcelData, ZipUpload

class Command(BaseCommand):
    help = 'Check imported data from ZIP files'

    def handle(self, *args, **options):
        # Check ZIP uploads
        uploads = ZipUpload.objects.all()
        self.stdout.write(f'ZIP uploads: {uploads.count()}')
        for upload in uploads:
            self.stdout.write(
                f'- {upload.file.name}: {upload.records_imported} records'
            )

        # Check Excel data
        records = ExcelData.objects.all()
        self.stdout.write(f'\nTotal records: {records.count()}')
        
        # Show sample records
        self.stdout.write('\nRecent records:')
        for record in records.order_by('-created_at')[:5]:
            self.stdout.write(
                f'\nName: {record.name}'
                f'\nJob: {record.job_title}'
                f'\nEmail: {record.email_id}'
                f'\n-------------------'
            )