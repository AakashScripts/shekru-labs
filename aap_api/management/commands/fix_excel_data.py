from django.core.management.base import BaseCommand
from aap_api.models import ExcelData, UploadedZip
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Fix Excel data import issues'

    def handle(self, *args, **options):
        # Check current data state
        self.stdout.write('Checking current data state...')
        total_records = ExcelData.objects.count()
        filled_records = ExcelData.objects.exclude(
            name='',
            job_title='',
            email_id='',
            phone_number='',
            current_location='',
            total_experience='',
            current_company_name=''
        ).count()

        self.stdout.write(f'Total records: {total_records}')
        self.stdout.write(f'Records with data: {filled_records}')

        # Process unprocessed uploads
        uploads = UploadedZip.objects.filter(processed=False)
        self.stdout.write(f'\nFound {uploads.count()} unprocessed uploads')

        for upload in uploads:
            try:
                if upload.zip_file and os.path.exists(upload.zip_file.path):
                    df = pd.read_excel(upload.zip_file.path)
                    records_created = 0

                    # Map column names (case-insensitive)
                    columns = {col.lower(): col for col in df.columns}
                    
                    for _, row in df.iterrows():
                        ExcelData.objects.create(
                            name=str(row.get(columns.get('name', 'Name'), '')).strip(),
                            job_title=str(row.get(columns.get('job title', 'Job Title'), '')).strip(),
                            email_id=str(row.get(columns.get('email', 'Email ID'), '')).strip(),
                            phone_number=str(row.get(columns.get('phone', 'Phone Number'), '')).strip(),
                            current_location=str(row.get(columns.get('location', 'Current Location'), '')).strip(),
                            total_experience=str(row.get(columns.get('experience', 'Total Experience'), '')).strip(),
                            current_company_name=str(row.get(columns.get('company', 'Current Company'), '')).strip(),
                            is_visible=True
                        )
                        records_created += 1

                    upload.processed = True
                    upload.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully processed {records_created} records from {upload.zip_file.name}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing {upload.zip_file.name}: {str(e)}'
                    )
                )