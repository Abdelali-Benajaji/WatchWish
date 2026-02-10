import requests
import re

def verify_new_ui_elements():
    print("Verifying UI elements...")
    
    # 1. Check "For You" page message (assuming we can hit it or mocking auth)
    # Since it's behind login, we might need to use session cookie or just verify the template file content which we already wrote.
    # But let's try to verify the file content directly for key strings to be sure.
    
    with open('backend/movies/templates/user_recommendations.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if "Your recommendations are not ready" in content:
            print("SUCCESS: Cold start message found in template.")
        else:
            print("FAILURE: Cold start message NOT found in template.")
            
    with open('backend/movies/templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if "star-rating" in content and "rateMovie" in content:
            print("SUCCESS: Star rating widget found in index template.")
        else:
             print("FAILURE: Star rating widget NOT found in index template.")

if __name__ == "__main__":
    verify_new_ui_elements()
