import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend root is on Python search path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load .env from backend/ or workspace root
load_dotenv(dotenv_path=BACKEND_DIR / ".env")
load_dotenv(dotenv_path=BACKEND_DIR.parent / ".env")
load_dotenv()

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
