import requests
import os

# Base URL of your API
BASE_URL = 'http://127.0.0.1:8088'  # Change this to match your server

def upload_single_excel(excel_file_path):
    """
    Upload a single Excel file
    """
    url = f'{BASE_URL}/api/import/'
    
    # Ensure file exists
    if not os.path.exists(excel_file_path):
        print(f"File not found: {excel_file_path}")
        return
    
    # Open and upload the file
    with open(excel_file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
    
    # Print response
    print("Single File Upload Response:")
    print(response.status_code)
    print(response.json())

def upload_zip_file(zip_file_path):
    """
    Upload a ZIP file containing multiple Excel files
    """
    url = f'{BASE_URL}/api/import-zip/'
    
    # Ensure file exists
    if not os.path.exists(zip_file_path):
        print(f"File not found: {zip_file_path}")
        return
    
    # Open and upload the file
    with open(zip_file_path, 'rb') as file:
        files = {'zip_file': file}
        response = requests.post(url, files=files)
    
    # Print response
    print("ZIP File Upload Response:")
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    # Example usage:
    
    # 1. Upload single Excel file
    excel_file = "D:/api/api/fresher.xlsx.xlsx"  # Change this to your Excel file path
    upload_single_excel(excel_file)
    
    # 2. Upload ZIP file containing multiple Excel files
    zip_file = "D:/api/api/excel zip.zip"    # Change this to your ZIP file path
    upload_zip_file(zip_file)
