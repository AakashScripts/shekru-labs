# Generated by Django 5.1.6 on 2025-03-10 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aap_api', '0006_rename_total_records_zipupload_records_imported_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zipupload',
            name='file',
            field=models.FileField(help_text='Upload ZIP file containing Excel files', upload_to='zip_uploads/'),
        ),
    ]
