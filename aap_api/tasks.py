from celery import shared_task
import openpyxl
from django.db import transaction, connections
from celery.utils.log import get_task_logger
from .models import ExcelData
import zipfile
import io
import pandas as pd
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
import numpy as np
from django.db import connection
import multiprocessing
import gc
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Optimize constants for better performance
CHUNK_SIZE = 50000  # Increased chunk size for faster reading
BATCH_SIZE = 10000  # Increased batch size for faster database inserts
MAX_WORKERS = max(multiprocessing.cpu_count() - 1, 1)  # Use all available CPU cores except one

def clean_data(value):
    """Clean and standardize data values"""
    if pd.isna(value) or value is None:
        return ''
    return str(value).strip()

def parse_date(value):
    """Parse date values efficiently"""
    if pd.isna(value):
        return None
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date()
    return None

def process_dataframe_chunk(chunk_data):
    """Process a chunk of DataFrame data efficiently"""
    try:
        # Pre-process data in memory
        records = []
        for _, row in chunk_data.iterrows():
            record = ExcelData(
                job_title=clean_data(row.get('job_title')),
                date_of_application=parse_date(row.get('date_of_application')),
                name=clean_data(row.get('name')),
                email_id=clean_data(row.get('email_id')),
                phone_number=clean_data(row.get('phone_number')),
                current_location=clean_data(row.get('current_location')),
                preferred_locations=clean_data(row.get('preferred_locations')),
                total_experience=clean_data(row.get('total_experience')),
                current_company_name=clean_data(row.get('current_company_name')),
                current_company_designation=clean_data(row.get('current_company_designation')),
                department=clean_data(row.get('department')),
                role=clean_data(row.get('role')),
                industry=clean_data(row.get('industry'))
            )
            records.append(record)

        # Bulk create in transaction
        with transaction.atomic():
            ExcelData.objects.bulk_create(
                records,
                batch_size=BATCH_SIZE,
                ignore_conflicts=True
            )
        
        processed_count = len(records)
        del records
        gc.collect()
        return processed_count
    except Exception as e:
        logger.error(f"Error processing chunk: {str(e)}")
        return 0

def process_excel_file_parallel(file_path):
    """Process Excel file using parallel processing"""
    try:
        # Read Excel file in chunks
        chunks = pd.read_excel(
            file_path,
            engine='openpyxl',
            chunksize=CHUNK_SIZE,
            dtype=str,  # Convert all to string for faster processing
            na_filter=False  # Don't convert empty strings to NaN
        )
        
        total_processed = 0
        
        # Process chunks in parallel using ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            
            for chunk in chunks:
                future = executor.submit(process_dataframe_chunk, chunk)
                futures.append(future)
            
            # Collect results
            for future in futures:
                try:
                    result = future.result()
                    total_processed += result
                except Exception as e:
                    logger.error(f"Error processing chunk: {str(e)}")
        
        return total_processed
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise

@shared_task(bind=True)
def process_zip_file(self, zip_file_path):
    """Process ZIP file containing Excel files with optimized parallel processing"""
    total_processed = 0
    results = []
    
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Get list of Excel files
            excel_files = [f for f in zip_ref.namelist() if f.lower().endswith(('.xlsx', '.xls'))]
            total_files = len(excel_files)
            
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract all files at once
                zip_ref.extractall(temp_dir)
                
                # Process files in parallel using ProcessPoolExecutor
                with ProcessPoolExecutor(max_workers=max(MAX_WORKERS // 2, 1)) as executor:
                    futures = []
                    
                    # Submit all files for processing
                    for excel_file in excel_files:
                        file_path = os.path.join(temp_dir, excel_file)
                        future = executor.submit(process_excel_file_parallel, file_path)
                        futures.append((excel_file, future))
                    
                    # Monitor progress and collect results
                    for excel_file, future in futures:
                        try:
                            file_processed = future.result()
                            total_processed += file_processed
                            
                            results.append({
                                'file': excel_file,
                                'records_processed': file_processed,
                                'status': 'success'
                            })
                            
                            # Update progress
                            progress = (len(results) / total_files) * 100
                            self.update_state(
                                state='PROGRESS',
                                meta={
                                    'current_file': excel_file,
                                    'progress': progress,
                                    'total_processed': total_processed,
                                    'total_files': total_files,
                                    'processed_files': len(results)
                                }
                            )
                            
                        except Exception as e:
                            logger.error(f"Error processing {excel_file}: {str(e)}")
                            results.append({
                                'file': excel_file,
                                'error': str(e),
                                'status': 'error'
                            })
        
        # Clean up
        try:
            os.unlink(zip_file_path)
        except Exception as e:
            logger.error(f"Error deleting zip file: {str(e)}")
        
        gc.collect()
        
        return {
            'status': 'completed',
            'total_processed': total_processed,
            'total_files': total_files,
            'successful_files': len([r for r in results if r['status'] == 'success']),
            'failed_files': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error processing zip file: {str(e)}")
        raise

@shared_task(bind=True)
def process_excel_file(self, file_path):
    """Process single Excel file using optimized processing"""
    try:
        total_processed = process_excel_file_parallel(file_path)
        
        # Clean up
        try:
            os.unlink(file_path)
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
        
        return {
            'status': 'success',
            'total_processed': total_processed
        }
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise

# You can safely delete this file or keep it with minimal functionality
import pandas as pd

def process_excel_file(file_path):
    df = pd.read_excel(file_path)
    return df.to_dict('records')