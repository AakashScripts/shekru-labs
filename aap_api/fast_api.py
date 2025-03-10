from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from django.core.wsgi import get_wsgi_application
import django
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from aap_api.models import ExcelData

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

async def process_chunk(df_chunk):
    """Process a chunk of DataFrame data"""
    records = df_chunk.to_dict('records')
    
    # Create ExcelData objects in bulk
    excel_data_objects = [
        ExcelData(
            job_title=record.get('job_title'),
            date_of_application=record.get('date_of_application'),
            name=record.get('name'),
            email_id=record.get('email_id'),
            phone_number=record.get('phone_number'),
            current_location=record.get('current_location'),
            preferred_locations=record.get('preferred_locations'),
            total_experience=record.get('total_experience'),
            current_company_name=record.get('current_company_name'),
            current_company_designation=record.get('current_company_designation'),
            department=record.get('department'),
            role=record.get('role'),
            industry=record.get('industry')
        ) for record in records
    ]
    
    # Bulk create the objects
    await asyncio.to_thread(ExcelData.objects.bulk_create, excel_data_objects)

@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...)):
    try:
        # Read Excel file in chunks
        chunk_size = 1000  # Adjust based on your needs
        chunks = pd.read_excel(file.file, chunksize=chunk_size)
        
        # Process chunks in parallel
        tasks = []
        for chunk in chunks:
            task = asyncio.create_task(process_chunk(chunk))
            tasks.append(task)
        
        # Wait for all chunks to be processed
        await asyncio.gather(*tasks)
        
        return {"message": "File processed successfully"}
    except Exception as e:
        return {"error": str(e)}