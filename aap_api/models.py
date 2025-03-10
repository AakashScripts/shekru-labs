from django.db import models
from django.core.mail import send_mass_mail
from django.conf import settings
from typing import Dict, Any
import os
import zipfile
from django.core.files.storage import default_storage
import pandas as pd  # For processing Excel/CSV
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Create your models here.

class ExcelData(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    email_id = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    current_location = models.CharField(max_length=100, null=True, blank=True)
    total_experience = models.CharField(max_length=50, null=True, blank=True)
    current_company_name = models.CharField(max_length=255, null=True, blank=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name or 'Unnamed'} - {self.email_id or 'No Email'}"

    def soft_delete(self):
        self.is_active = False
        self.save()
    
    def restore(self):
        self.is_active = True
        self.save()

def validate_excel_file(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in ['.xlsx', '.xls']:
        raise ValidationError('Only Excel files (.xlsx, .xls) are allowed.')

class UploadedExcel(models.Model):
    file = models.FileField(
        upload_to='excel_uploads/',
        validators=[validate_excel_file],
        help_text='Upload Excel file (.xlsx, .xls)'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    file_name = models.CharField(max_length=255, blank=True)
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
        super().save(*args, **kwargs)

    def process_file(self):
        if not self.file:
            raise ValueError("No file uploaded")

        try:
            df = pd.read_excel(self.file.path)
            records_created = 0

            # Column mappings (case-insensitive)
            mappings = {
                'name': ['name', 'full name', 'candidate name'],
                'job_title': ['job title', 'position', 'role'],
                'email_id': ['email', 'email id', 'email address'],
                'phone_number': ['phone', 'phone number', 'mobile'],
                'current_location': ['location', 'current location', 'city'],
                'total_experience': ['experience', 'total experience', 'exp'],
                'current_company_name': ['company', 'current company', 'organization']
            }

            # Find matching columns
            column_map = {}
            df_columns = [col.lower().strip() for col in df.columns]
            for field, possible_names in mappings.items():
                for name in possible_names:
                    if name in df_columns:
                        column_map[field] = df.columns[df_columns.index(name)]
                        break

            if not column_map:
                raise ValueError("No matching columns found in Excel file")

            # Create records
            for _, row in df.iterrows():
                data = {}
                for field, excel_col in column_map.items():
                    data[field] = str(row.get(excel_col, '')).strip()

                ExcelData.objects.create(
                    name=data.get('name', ''),
                    job_title=data.get('job_title', ''),
                    email_id=data.get('email_id', ''),
                    phone_number=data.get('phone_number', ''),
                    current_location=data.get('current_location', ''),
                    total_experience=data.get('total_experience', ''),
                    current_company_name=data.get('current_company_name', ''),
                    is_visible=True
                )
                records_created += 1

            self.processed = True
            self.save()
            return records_created

        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

    def __str__(self):
        return f"Excel Upload - {self.file_name}"

class DownloadHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    download_time = models.DateTimeField(auto_now_add=True)
    filters = models.JSONField()  # Store filters as JSON
    record_count = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.download_time.strftime('%Y-%m-%d %H:%M')}"
    
class UploadedZip(models.Model):
    zip_file = models.FileField(upload_to='zip_uploads/')
    file_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)  # Fixed the syntax error here

    def save(self, *args, **kwargs):
        if self.zip_file:
            self.file_name = os.path.basename(self.zip_file.name)
        super().save(*args, **kwargs)

    def process_zip(self):
        try:
            with zipfile.ZipFile(self.zip_file.path, 'r') as zip_ref:
                temp_dir = os.path.join('media', 'temp_extracts', str(self.id))
                os.makedirs(temp_dir, exist_ok=True)
                
                zip_ref.extractall(temp_dir)
                records_created = 0
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.xlsx', '.xls')):
                            excel_path = os.path.join(root, file)
                            df = pd.read_excel(excel_path)
                            
                            for _, row in df.iterrows():
                                ExcelData.objects.create(
                                    name=str(row.get('Name', '')).strip(),
                                    job_title=str(row.get('Job Title', '')).strip(),
                                    email_id=str(row.get('Email', '')).strip(),
                                    phone_number=str(row.get('Phone', '')).strip(),
                                    current_location=str(row.get('Location', '')).strip(),
                                    total_experience=str(row.get('Experience', '')).strip(),
                                    current_company_name=str(row.get('Company', '')).strip(),
                                    is_visible=True
                                )
                                records_created += 1
                
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                self.processed = True
                self.save()
                
                return records_created
                
        except Exception as e:
            raise Exception(f"Error processing zip file: {str(e)}")

    def __str__(self):
        return f"Zip Upload - {self.file_name or 'Unnamed'}"

def validate_zip_file(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.zip':
        raise ValidationError('Only ZIP files (.zip) are allowed.')

class ZipUpload(models.Model):
    file = models.FileField(
        upload_to='zip_uploads/',
        help_text='Upload ZIP file containing Excel files (.xlsx, .xls)'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    total_records = models.IntegerField(default=0)

    def process_zip(self):
        try:
            temp_dir = os.path.join('media', 'temp_extracts', str(self.id))
            os.makedirs(temp_dir, exist_ok=True)
            records_created = 0

            with zipfile.ZipFile(self.file.path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.xlsx', '.xls')):
                            file_path = os.path.join(root, file)
                            records_created += self._process_excel(file_path)

            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

            self.processed = True
            self.total_records = records_created
            self.save()
            return records_created

        except Exception as e:
            logger.error(f"Error processing ZIP {self.file.name}: {str(e)}")
            raise

    def _process_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            records_created = 0

            # Map column names
            column_maps = {
                'name': ['Name', 'Full Name', 'Candidate Name'],
                'job_title': ['Job Title', 'Position', 'Role'],
                'email_id': ['Email', 'Email ID', 'Email Address'],
                'phone_number': ['Phone', 'Phone Number', 'Mobile'],
                'current_location': ['Location', 'Current Location', 'City'],
                'total_experience': ['Experience', 'Total Experience', 'Years'],
                'current_company_name': ['Company', 'Current Company', 'Organization']
            }

            # Find matching columns
            field_mapping = {}
            excel_columns = [col.strip() for col in df.columns]
            for field, possible_names in column_maps.items():
                for name in possible_names:
                    if name in excel_columns:
                        field_mapping[field] = name
                        break

            # Process each row
            for _, row in df.iterrows():
                ExcelData.objects.create(
                    name=str(row.get(field_mapping.get('name', 'Name'), '')).strip(),
                    job_title=str(row.get(field_mapping.get('job_title', 'Job Title'), '')).strip(),
                    email_id=str(row.get(field_mapping.get('email_id', 'Email'), '')).strip(),
                    phone_number=str(row.get(field_mapping.get('phone_number', 'Phone'), '')).strip(),
                    current_location=str(row.get(field_mapping.get('current_location', 'Location'), '')).strip(),
                    total_experience=str(row.get(field_mapping.get('total_experience', 'Experience'), '')).strip(),
                    current_company_name=str(row.get(field_mapping.get('current_company_name', 'Company'), '')).strip(),
                    is_visible=True
                )
                records_created += 1

            return records_created

        except Exception as e:
            logger.error(f"Error processing Excel {file_path}: {str(e)}")
            raise

    def __str__(self):
        return f"ZIP Upload - {self.file.name}"

class ZipUpload(models.Model):
    file = models.FileField(
        upload_to='zip_uploads/',
        help_text='Upload ZIP file containing Excel files'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    records_imported = models.IntegerField(default=0)

    def __str__(self):
        return f"ZIP Upload - {self.file.name}"

    def process_zip(self):
        try:
            temp_dir = os.path.join('media', 'temp_extracts', str(self.id))
            os.makedirs(temp_dir, exist_ok=True)
            total_imported = 0

            with zipfile.ZipFile(self.file.path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.xlsx', '.xls')):
                            excel_path = os.path.join(root, file)
                            imported = self._process_excel(excel_path)
                            total_imported += imported

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)

            self.records_imported = total_imported
            self.processed = True
            self.save()
            return total_imported

        except Exception as e:
            raise Exception(f"Error processing ZIP: {str(e)}")

    def _process_excel(self, excel_path):
        try:
            df = pd.read_excel(excel_path)
            records_created = 0

            for _, row in df.iterrows():
                ExcelData.objects.create(
                    name=str(row.get('Name', '')).strip(),
                    job_title=str(row.get('Job Title', '')).strip(),
                    email_id=str(row.get('Email', '')).strip(),
                    phone_number=str(row.get('Phone', '')).strip(),
                    current_location=str(row.get('Location', '')).strip(),
                    total_experience=str(row.get('Experience', '')).strip(),
                    current_company_name=str(row.get('Company', '')).strip(),
                    is_visible=True
                )
                records_created += 1

            return records_created

        except Exception as e:
            raise Exception(f"Error processing Excel {os.path.basename(excel_path)}: {str(e)}")