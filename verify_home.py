import requests
import sys

def verify_home_page():
    print("Verifying Home Page Content...")
    try:
        response = requests.get('http://127.0.0.1:8000/')
        content = response.text
        
        if "Explore Popular Movies" in content:
            print("SUCCESS: 'Explore Popular Movies' section found.")
        else:
            print("FAILURE: 'Explore Popular Movies' section NOT found.")
            
        if "Enter a movie title (e.g., Unbeatable, Broken)" in content:
             print("SUCCESS: Updated placeholder found.")
        else:
             print("FAILURE: Updated placeholder NOT found.")
             
    except Exception as e:
        print(f"Error accessing home page: {e}")

if __name__ == "__main__":
    verify_home_page()
