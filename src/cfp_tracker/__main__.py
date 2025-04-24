import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    """Run the application"""
    uvicorn.run(
        "cfp_tracker.api.app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        reload_dirs=["src"],
        factory=False
    )

if __name__ == "__main__":
    main() 