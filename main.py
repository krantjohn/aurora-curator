import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path

from config import SERVER_HOST, SERVER_PORT, DATA_ROOT
from database import init_db, get_connection
from api.characters import router as characters_router
from api.images import router as images_router, media_router
from api.tasks import router as tasks_router
from api.storage import router as storage_router
from api.settings import router as settings_router
from api.google_auth import router as google_auth_router
from api.auth import router as auth_router, verify_request_access

# Configure Rotating Logs
LOGS_DIR = DATA_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOGS_DIR / "app.log"

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
root_logger.addHandler(console_handler)

# Rotating file handler (10MB x 5 files)
file_handler = RotatingFileHandler(str(log_file), maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
root_logger.addHandler(file_handler)

logger = logging.getLogger("anime_gallery.main")

NGINX_404_HTML = """<!DOCTYPE html>
<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Anime Gallery Manager backend...")
    init_db()
    logger.info(f"Data root: {DATA_ROOT}")
    yield
    logger.info("Shutting down Anime Gallery Manager backend...")

app = FastAPI(
    title="Anime Gallery Manager",
    description="动漫图片智能收集与筛选管理系统",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,    # Disable public Swagger docs for stealth
    redoc_url=None,   # Disable public ReDoc for stealth
    openapi_url=None  # Disable OpenAPI schema for stealth
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# High-Performance Gzip compression for all responses
app.add_middleware(GZipMiddleware, minimum_size=500)

import time
from collections import defaultdict

# IP Throttle Tracking for unauthorized scan/fuzz protection
UNAUTH_IP_TRACKER = defaultdict(list)

@app.middleware("http")
async def stealth_cloaking_middleware(request: Request, call_next):
    """
    Ultra-Stealth Device Authorization & 404 Cloaking Middleware.
    1. If request carries valid 10-year token or Master Magic Key: Allows seamless full access.
    2. If request is from unauthenticated internet visitor/scanner: Returns standard realistic Nginx 404 Not Found.
    """
    is_authorized, new_token = verify_request_access(request)

    if not is_authorized:
        # Rate limit & slow down scanner bots
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        UNAUTH_IP_TRACKER[ip] = [t for t in UNAUTH_IP_TRACKER[ip] if now - t < 60]
        UNAUTH_IP_TRACKER[ip].append(now)

        if len(UNAUTH_IP_TRACKER[ip]) > 10:
            import asyncio
            await asyncio.sleep(1.0)  # Throttles dictionary scanners

        # Full Cloaking: Return authentic Ubuntu Nginx 404 Not Found page
        return HTMLResponse(
            content=NGINX_404_HTML,
            status_code=404,
            headers={
                "Server": "nginx/1.24.0 (Ubuntu)",
                "Content-Type": "text/html",
                "X-Robots-Tag": "noindex, nofollow, noarchive, nosnippet",
                "Referrer-Policy": "no-referrer"
            }
        )

    # Proceed to app / API handler
    response = await call_next(request)

    # If this was a new device activation via magic link, set 10-year persistent cookie
    if new_token:
        response.set_cookie(
            key="auth_token",
            value=new_token,
            max_age=315360000, # 10 Years in seconds
            path="/",
            httponly=False,
            samesite="lax",
            secure=True
        )

    return response

# Include API Routers
app.include_router(auth_router)
app.include_router(characters_router)
app.include_router(images_router)
app.include_router(media_router)
app.include_router(tasks_router)
app.include_router(storage_router)
app.include_router(settings_router)
app.include_router(google_auth_router)

# Mount Static assets
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/character/{path:path}", methods=["GET", "HEAD"])
@app.api_route("/favorites", methods=["GET", "HEAD"])
@app.api_route("/favorites/{path:path}", methods=["GET", "HEAD"])
@app.api_route("/settings", methods=["GET", "HEAD"])
@app.api_route("/characters", methods=["GET", "HEAD"])
async def serve_spa(request: Request, path: str = ""):
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse(content=NGINX_404_HTML, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)
