import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from aap_api.models import ExcelData

def check_database():
    """
    Check if there's any data in the ExcelData table
    """
    # Get total count
    total_records = ExcelData.objects.count()
    print(f"\nTotal records in database: {total_records}")
    
    # Get some sample records
    if total_records > 0:
        print("\nSample records:")
        for record in ExcelData.objects.all()[:5]:  # Show first 5 records
            print(f"- Name: {record.name}")
            print(f"  Job Title: {record.job_title}")
            print(f"  Email: {record.email_id}")
            print("---")
    else:
        print("\nNo records found in the database!")

if __name__ == "__main__":
    check_database()
