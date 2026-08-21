import os
import sys
import traceback
from pathlib import Path

# Add project root to sys.path so backend/, rag/, llm/, gemini/ are importable
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from backend.main import app
except Exception as e:
    # If the real app fails to load, create a diagnostic app
    # that shows us the actual error instead of a blank 500
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()
    _startup_error = traceback.format_exc()

    @app.get("/{path:path}")
    async def catch_all(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "App failed to start",
                "detail": str(e),
                "traceback": _startup_error,
                "python_version": sys.version,
                "sys_path": sys.path[:5],
                "cwd": os.getcwd(),
                "files_in_root": os.listdir(str(BASE_DIR))[:20] if BASE_DIR.exists() else "BASE_DIR not found",
            }
        )

