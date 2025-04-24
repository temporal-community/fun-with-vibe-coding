import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "src.cfp_tracker.api.app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=8001,
        reload=True
    ) 