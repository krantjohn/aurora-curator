from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from database import get_connection
from models import SettingUpdate
from providers.google_photos import GooglePhotosProvider

router = APIRouter(prefix="/api/settings", tags=["Settings"])
google_photos = GooglePhotosProvider()

@router.get("")
async def get_settings():
    conn = get_connection()
    rows = conn.execute("SELECT key, value, description FROM settings").fetchall()
    conn.close()
    
    settings_dict = {}
    for r in rows:
        val = r["value"]
        # Mask sensitive keys partially for UI display
        if "secret" in r["key"] or "refresh_token" in r["key"]:
            masked = f"{val[:6]}...{val[-4:]}" if len(val) > 12 else ("******" if val else "")
            settings_dict[r["key"]] = {"value": val, "masked": masked, "description": r["description"]}
        else:
            settings_dict[r["key"]] = {"value": val, "masked": val, "description": r["description"]}
            
    return settings_dict

@router.post("")
async def update_settings(req: SettingUpdate):
    conn = get_connection()
    for k, v in req.settings.items():
        conn.execute("""
            INSERT INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
        """, (k, v.strip()))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Settings updated successfully"}

@router.post("/google-photos/sync")
async def sync_google_photos():
    """Triggers Google Photos sync for all favorites."""
    if not google_photos.is_configured:
        return {
            "status": "warning",
            "message": "Google Photos 尚未完成 OAuth 连接，请先点击【🔗 一键授权连接 Google 账号】"
        }
    return await google_photos.sync_all_favorites()
