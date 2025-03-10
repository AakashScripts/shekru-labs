import requests

def test_sheet_access():
    """
    Test accessing the sheet view
    """
    url = 'http://127.0.0.1:8088/api/sheet/'
    
    print("Testing sheet access...")
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('content-type', 'Not specified')}")
    
    if response.status_code == 200:
        print("\nSuccess! The sheet is accessible.")
        # Save the response to a file for inspection
        with open('sheet_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Response saved to 'sheet_response.html'")
    else:
        print(f"\nError accessing the sheet: {response.status_code}")
        print("Response content:")
        print(response.text)

if __name__ == "__main__":
    test_sheet_access()
