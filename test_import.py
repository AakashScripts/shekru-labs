import requests
import json
from pathlib import Path

def test_zip_import():
    """
    Test importing Excel files from a ZIP archive
    """
    # API endpoint
    url = 'http://127.0.0.1:8088/api/import-zip/'
    
    # Path to your ZIP file
    zip_file_path = 'D:/api/api/excel zip.zip'  # Replace with your ZIP file path
    
    if not Path(zip_file_path).exists():
        print(f"Error: ZIP file not found at {zip_file_path}")
        return
    
    # Upload the ZIP file
    with open(zip_file_path, 'rb') as zip_file:
        files = {'zip_file': zip_file}
        print("Uploading ZIP file...")
        response = requests.post(url, files=files)
    
    # Print the response
    print("\nResponse Status:", response.status_code)
    try:
        print("\nResponse Content:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Raw response:", response.text)
    
    # If successful, check the imported data
    if response.status_code == 200:
        # Get the list of imported records
        list_url = 'http://127.0.0.1:8088/api/data/'
        print("\nFetching imported records...")
        list_response = requests.get(list_url)
        
        if list_response.status_code == 200:
            data = list_response.json()
            print(f"\nTotal records in database: {data['count']}")
            print("\nSample of imported records:")
            for item in data['results'][:5]:  # Show first 5 records
                print(f"- {item['name']} ({item['job_title']})")
        else:
            print("Error fetching records:", list_response.status_code)

if __name__ == "__main__":
    test_zip_import()
