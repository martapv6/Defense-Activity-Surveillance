import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from contextlib import asynccontextmanager

# --- Ensure ALL model files are imported here to register them with SQLAlchemy ---
# This ensures classes like 'AreaOfInterest' are visible when 'User' is configured. -ma enerveaza import-urile astea da fara ele nu mergea sa creez prima data tabelele:(
import src.models.user
import src.models.aoi 
import src.models.image
import src.models.model_ai
import src.models.detection
import src.models.alert

from src.core.gee_auth import initialize_gee
from src.core.database import create_db_and_tables
from src.core.seeder import seed_initial_data

from src.api import user as user_api

@asynccontextmanager
async def lifespan(app: FastAPI):

    initialize_gee() #function that initializes the GEE Api through our credentials


    await create_db_and_tables() #the function that creates the tables

    await seed_initial_data() #in order to have some default values to start

    # The 'yield' pauses the function and FastAPI starts serving requests
    yield
    print("Application shutdown sequence initiated...")
    # Add any cleanup logic here, though GEE often doesn't require explicit cleanup
    # Example: cleanup_database_connection()
    print("Application shutdown complete.")


app = FastAPI(lifespan=lifespan)
@app.get("/")
async def root():
    return {"message": "Satlas Detector API is running and GEE is initialized."}

app.include_router(user_api.router, prefix="/api")