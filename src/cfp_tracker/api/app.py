from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .endpoints import ingestion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CFP Tracker API",
    description="API for tracking and managing Call for Papers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["ingestion"])

@app.get("/")
async def root():
    return {"message": "Welcome to CFP Tracker API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 