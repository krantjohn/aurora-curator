import urllib.parse
import httpx
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from database import get_connection

logger = logging.getLogger("anime_gallery.api.google_auth")

router = APIRouter(prefix="/api/google", tags=["Google OAuth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = "https://www.googleapis.com/auth/photoslibrary https://www.googleapis.com/auth/photoslibrary.sharing"

@router.get("/auth-url")
async def get_google_auth_url(request: Request):
    """Generates the Google OAuth 2.0 consent URL using stored client credentials."""
    conn = get_connection()
    c_id_row = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_client_id'").fetchone()
    conn.close()

    if not c_id_row or not c_id_row["value"]:
        raise HTTPException(status_code=400, detail="请先在设置中填写 Google Client ID 并保存")

    client_id = c_id_row["value"].strip()
    host = request.headers.get("host") or (request.client.host if request.client else "localhost:8088")
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    path_prefix = "/gallery" if "/gallery" in request.url.path else ""
    redirect_uri = f"{proto}://{host}{path_prefix}/api/google/callback"

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent"
    }

    url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return {"auth_url": url, "redirect_uri": redirect_uri}

@router.get("/callback")
async def google_oauth_callback(code: str, request: Request):
    """Handles Google OAuth authorization code exchange and automatically saves the Refresh Token."""
    conn = get_connection()
    c_id_row = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_client_id'").fetchone()
    c_sec_row = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_client_secret'").fetchone()

    if not c_id_row or not c_sec_row or not c_id_row["value"] or not c_sec_row["value"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Missing Google OAuth Client credentials in settings")

    client_id = c_id_row["value"].strip()
    client_secret = c_sec_row["value"].strip()

    host = request.headers.get("host") or (request.client.host if request.client else "localhost:8088")
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    path_prefix = "/gallery" if "/gallery" in request.url.path else ""
    redirect_uri = f"{proto}://{host}{path_prefix}/api/google/callback"

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GOOGLE_TOKEN_URL, data=data)
            if resp.status_code != 200:
                logger.error(f"Failed to exchange Google OAuth code: {resp.text}")
                conn.close()
                return RedirectResponse(url="/gallery/?auth_error=google_token_exchange_failed")

            token_data = resp.json()
            refresh_token = token_data.get("refresh_token")
            if refresh_token:
                conn.execute("INSERT INTO settings (key, value) VALUES ('google_photos_refresh_token', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (refresh_token,))
                conn.commit()
                logger.info("Successfully received and stored Google Photos OAuth refresh_token!")
            conn.close()

            return RedirectResponse(url="/gallery/?auth_success=google_connected")
    except Exception as e:
        logger.error(f"Exception during Google OAuth callback: {e}")
        conn.close()
        return RedirectResponse(url="/gallery/?auth_error=exception")
