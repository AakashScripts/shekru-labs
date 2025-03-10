import requests
from pathlib import Path

def import_excel_file():
    """Import data from Excel file to the API"""
    # API endpoint - make sure server is running on this port
    url = 'http://127.0.0.1:8088/api/import-excel/'
    
    # Excel file path
    excel_file = 'fresher.xlsx.xlsx'
    
    if not Path(excel_file).exists():
        print(f"Error: Excel file '{excel_file}' not found!")
        return
    
    print(f"Found Excel file: {excel_file}")
    print("Starting import process...")
    
    try:
        # Open and upload the file
        with open(excel_file, 'rb') as f:
            files = {'excel_file': f}
            print("Uploading file to server...")
            response = requests.post(url, files=files)
        
        # Check response
        print('\nStatus Code:', response.status_code)
        if response.status_code == 200:
            print('Import successful!')
            try:
                result = response.json()
                print(f"Imported {result.get('count', 0)} records")
            except:
                print('Response:', response.text)
        else:
            print('Import failed!')
            print('Response:', response.text)
            
        # Verify data was imported
        verify_url = 'http://127.0.0.1:8088/api/data/'
        print("\nVerifying imported data...")
        verify_response = requests.get(verify_url)
        if verify_response.status_code == 200:
            data = verify_response.json()
            if isinstance(data, list):
                print(f"Found {len(data)} records in database")
            else:
                print(f"Found {data.get('count', 0)} records in database")
        else:
            print("Could not verify data import")
            
    except Exception as e:
        print('Error occurred:', str(e))
        print('Make sure the Django server is running on port 8088')

if __name__ == '__main__':
    import_excel_file()
