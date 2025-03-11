from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin
from .models import ExcelData, UploadedExcel, DownloadHistory, UploadedZip, ZipUpload
from django.contrib import messages
from django.db.models import Q
import pandas as pd
import zipfile
import os

# Customize the User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {queryset.count()} users.")
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {queryset.count()} users.")
    deactivate_users.short_description = "Deactivate selected users"

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register your other models
@admin.register(ExcelData)
class ExcelDataAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'job_title', 
        'email_id',
        'phone_number',
        'current_location',
        'total_experience'
    )  # Removed current_company_name
    
    list_filter = ('job_title', 'current_location')
    search_fields = ('name', 'email_id', 'phone_number')
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'current_company_name' in fields:
            fields.remove('current_company_name')
        return fields
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'current_company_name' in form.base_fields:
            del form.base_fields['current_company_name']
        return form

class ZipUploadAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at', 'processed')
    actions = ['process_zip_files']

    def process_zip_files(self, request, queryset):
        for upload in queryset:
            try:
                with zipfile.ZipFile(upload.file.path, 'r') as zip_ref:
                    temp_dir = os.path.join('media', 'temp_extracts', str(upload.id))
                    os.makedirs(temp_dir, exist_ok=True)
                    zip_ref.extractall(temp_dir)
                    
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            if file.endswith(('.xlsx', '.xls')):
                                excel_path = os.path.join(root, file)
                                df = pd.read_excel(excel_path)
                                
                                # Define column mappings
                                column_maps = {
                                    'Name': ['name', 'full name', 'candidate name'],
                                    'Job Title': ['job title', 'position', 'designation'],
                                    'Email': ['email', 'email id', 'email address'],
                                    'Phone': ['phone', 'phone number', 'mobile'],
                                    'Location': ['location', 'current location', 'city'],
                                    'Experience': ['experience', 'total experience', 'exp'],
                                    'Company': ['company', 'current company', 'organization']
                                }
                                
                                # Map Excel columns to model fields
                                field_mapping = {}
                                excel_columns = [col.lower().strip() for col in df.columns]
                                for field, variants in column_maps.items():
                                    for variant in variants:
                                        if variant in excel_columns:
                                            field_mapping[field] = df.columns[excel_columns.index(variant)]
                                            break
                                
                                # Process rows
                                for _, row in df.iterrows():
                                    ExcelData.objects.create(
                                        name=str(row.get(field_mapping.get('Name', 'Name'), '')).strip(),
                                        job_title=str(row.get(field_mapping.get('Job Title', 'Job Title'), '')).strip(),
                                        email_id=str(row.get(field_mapping.get('Email', 'Email'), '')).strip(),
                                        phone_number=str(row.get(field_mapping.get('Phone', 'Phone'), '')).strip(),
                                        current_location=str(row.get(field_mapping.get('Location', 'Location'), '')).strip(),
                                        total_experience=str(row.get(field_mapping.get('Experience', 'Experience'), '')).strip(),
                                        current_company_name=str(row.get(field_mapping.get('Company', 'Company'), '')).strip(),
                                        is_visible=True
                                    )
                
                    import shutil
                    shutil.rmtree(temp_dir)
                    
                    upload.processed = True
                    upload.save()
                    messages.success(request, f'Successfully processed {upload.file.name}')
                    
            except Exception as e:
                messages.error(request, f'Error processing {upload.file.name}: {str(e)}')

    process_zip_files.short_description = "Process selected ZIP files"

# Register models
admin.site.register(ZipUpload, ZipUploadAdmin)

@admin.register(UploadedExcel)
class UploadedExcelAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at', 'processed')
    list_filter = ('processed',)
    actions = ['import_excel_data']

    def import_excel_data(self, request, queryset):
        total_records = 0
        for upload in queryset:
            try:
                # Read Excel file
                df = pd.read_excel(upload.file.path)
                
                # Get column names from Excel
                excel_columns = df.columns.str.strip()
                
                # Define expected column mappings
                column_maps = {
                    'name': ['Name', 'Full Name', 'Candidate Name'],
                    'job_title': ['Job Title', 'Position', 'Role', 'Designation'],
                    'email_id': ['Email', 'Email ID', 'Email Address'],
                    'phone_number': ['Phone', 'Phone Number', 'Mobile', 'Contact'],
                    'current_location': ['Location', 'Current Location', 'City'],
                    'total_experience': ['Experience', 'Total Experience', 'Years of Experience'],
                    'current_company_name': ['Company', 'Current Company', 'Organization']
                }
                
                # Map Excel columns to model fields
                field_mapping = {}
                for field, possible_names in column_maps.items():
                    for name in possible_names:
                        if name in excel_columns.values:
                            field_mapping[field] = name
                            break
                
                records_created = 0
                # Process each row
                for _, row in df.iterrows():
                    try:
                        record = ExcelData.objects.create(
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
                    except Exception as row_error:
                        messages.warning(request, f'Error in row {_ + 2}: {str(row_error)}')
                        continue

                upload.processed = True
                upload.save()
                total_records += records_created
                messages.success(request, f'Successfully imported {records_created} records from {upload.file.name}')
                
            except Exception as e:
                messages.error(request, f'Error processing {upload.file.name}: {str(e)}')

        if total_records > 0:
            messages.info(request, f'Total {total_records} records imported. Check Excel Data section.')

    import_excel_data.short_description = "Import data from selected Excel files"

@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'download_time', 'record_count')
    list_filter = ('user',)
    ordering = ('-download_time',)

