import ee
import os

def initialize_gee():
    # Load credentials from environment variable pointing to the JSON file
    key_path = os.getenv("GEE_SERVICE_ACCOUNT_KEY")
    if key_path and os.path.exists(key_path):
        try:
            credentials = ee.ServiceAccountCredentials(
                os.getenv("GEE_SERVICE_ACCOUNT_EMAIL"),
                key_path
            )
            ee.Initialize(credentials=credentials)
            print("GEE initialized successfully with Service Account.")
        except Exception as e:
            print(f"GEE Initialization failed: {e}")
    else:
        # Fallback for local testing if preferred, but not for production
        ee.Initialize() 
        print("GEE initialized for local user.") 

# In app/main.py
from fastapi import FastAPI
app = FastAPI()
@app.on_event("startup")
def startup_event():
    initialize_gee()