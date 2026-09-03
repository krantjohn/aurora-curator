import os
import logging
import httpx
from typing import Optional, Dict, Any, List
from pathlib import Path
from database import get_connection

logger = logging.getLogger("anime_gallery.providers.google_photos")

class GooglePhotosProvider:
    """
    Google Photos Library API Sync Service Architecture.
    Allows seamless backup and sync of favorites (<character_name>/) to Google Photos Albums.
    """
    def __init__(self):
        self.auth_url = "https://oauth2.googleapis.com/token"
        self.api_base = "https://photoslibrary.googleapis.com/v1"

    @property
    def is_configured(self) -> bool:
        conn = get_connection()
        c_id = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_client_id'").fetchone()
        c_sec = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_client_secret'").fetchone()
        r_tok = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_refresh_token'").fetchone()
        conn.close()
        return bool(c_id and c_sec and r_tok and c_id["value"] and c_sec["value"] and r_tok["value"])

    async def get_access_token(self) -> Optional[str]:
        if not self.is_configured:
            return None
        
        conn = get_connection()
        c_id = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_client_id'").fetchone()["value"]
        c_sec = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_client_secret'").fetchone()["value"]
        r_tok = conn.execute("SELECT value FROM settings WHERE key = 'google_photos_refresh_token'").fetchone()["value"]
        conn.close()

        data = {
            "client_id": c_id,
            "client_secret": c_sec,
            "refresh_token": r_tok,
            "grant_type": "refresh_token"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.auth_url, data=data)
                if resp.status_code == 200:
                    return resp.json().get("access_token")
                else:
                    logger.error(f"Google Photos token refresh failed: {resp.text}")
        except Exception as e:
            logger.error(f"Google Photos authentication error: {e}")
        return None

    async def create_or_get_album(self, album_title: str) -> Optional[str]:
        """Creates a Google Photos album or retrieves an existing one by title."""
        token = await self.get_access_token()
        if not token:
            return None

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Check existing albums
                list_resp = await client.get(f"{self.api_base}/albums", headers=headers)
                if list_resp.status_code == 200:
                    albums = list_resp.json().get("albums", [])
                    for alb in albums:
                        if alb.get("title") == album_title:
                            return alb.get("id")

                # Create new album
                create_resp = await client.post(
                    f"{self.api_base}/albums",
                    headers=headers,
                    json={"album": {"title": album_title}}
                )
                if create_resp.status_code == 200:
                    return create_resp.json().get("id")
        except Exception as e:
            logger.error(f"Failed to get/create Google Photos album: {e}")
        return None

    async def upload_image(self, file_path: Path, album_id: str) -> bool:
        """Uploads a local favorite image to the designated Google Photos Album."""
        token = await self.get_access_token()
        if not token or not file_path.exists():
            return False

        upload_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
            "X-Goog-Upload-Content-Type": "image/jpeg",
            "X-Goog-Upload-Protocol": "raw"
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(file_path, "rb") as f:
                    content = f.read()

                # Step 1: Upload raw byte stream
                upload_resp = await client.post(
                    "https://photoslibrary.googleapis.com/v1/uploads",
                    headers=upload_headers,
                    content=content
                )
                if upload_resp.status_code != 200:
                    return False
                upload_token = upload_resp.text

                # Step 2: Add to Album
                create_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                batch_resp = await client.post(
                    f"{self.api_base}/mediaItems:batchCreate",
                    headers=create_headers,
                    json={
                        "albumId": album_id,
                        "newMediaItems": [{
                            "description": f"Saved from Anime Gallery Manager - {file_path.stem}",
                            "simpleMediaItem": {"uploadToken": upload_token}
                        }]
                    }
                )
                return batch_resp.status_code == 200
        except Exception as e:
            logger.error(f"Google Photos upload error for {file_path}: {e}")
            return False

    async def sync_all_favorites(self) -> Dict[str, Any]:
        """Iterates over all saved images in DB and uploads them to Google Photos."""
        if not self.is_configured:
            return {"status": "error", "message": "Google Photos 未完成 OAuth 授权连接"}

        from config import FAVORITES_DIR
        conn = get_connection()
        saved_imgs = conn.execute("""
            SELECT i.id, i.favorites_path, i.filename, c.name as character_name, i.google_sync_status
            FROM images i
            JOIN characters c ON i.character_id = c.id
            WHERE i.status = 'saved'
        """).fetchall()

        if not saved_imgs:
            conn.close()
            return {"status": "info", "message": "收藏夹暂无图片，请先在工作台中收藏图片"}

        success_count = 0
        fail_count = 0
        album_cache = {}

        for img in saved_imgs:
            char_name = img["character_name"]
            fav_path = Path(img["favorites_path"]) if img["favorites_path"] else FAVORITES_DIR / char_name / img["filename"]

            if not fav_path.exists():
                continue

            # Get or create album for this character
            if char_name not in album_cache:
                album_id = await self.create_or_get_album(f"Anime - {char_name}")
                album_cache[char_name] = album_id
            else:
                album_id = album_cache[char_name]

            if not album_id:
                fail_count += 1
                continue

            ok = await self.upload_image(fav_path, album_id)
            if ok:
                success_count += 1
                conn.execute("UPDATE images SET google_sync_status = 'synced' WHERE id = ?", (img["id"],))
            else:
                fail_count += 1
                conn.execute("UPDATE images SET google_sync_status = 'failed' WHERE id = ?", (img["id"],))
            conn.commit()

        conn.close()
        return {
            "status": "success",
            "message": f"Google Photos 云端同步完成！成功同步 {success_count} 张原画至对应相册",
            "synced_count": success_count,
            "failed_count": fail_count
        }
