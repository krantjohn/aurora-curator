from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path
from database import get_connection
from models import ImageOut, BatchActionRequest
from services.storage_service import StorageService
from config import DATA_ROOT, TEMP_DIR, FAVORITES_DIR, CACHE_DIR

router = APIRouter(prefix="/api/images", tags=["Images"])

@router.get("", response_model=List[ImageOut])
async def list_images(
    character_id: Optional[int] = None,
    character_name: Optional[str] = None,
    status: Optional[str] = Query(None, description="pending, saved, all"),
    rating: Optional[str] = Query(None, description="sfw, r18, all"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    conn = get_connection()
    query = """
        SELECT i.*, c.name as character_name 
        FROM images i
        JOIN characters c ON i.character_id = c.id
        WHERE 1=1
    """
    params = []

    if character_id:
        query += " AND i.character_id = ?"
        params.append(character_id)
    elif character_name:
        clean_name = character_name.strip()
        query += " AND (c.name = ? OR c.slug = ?)"
        params.extend([clean_name, clean_name])

    if status and status != "all":
        query += " AND i.status = ?"
        params.append(status)
    else:
        # By default exclude deleted/cleaned
        query += " AND i.status IN ('pending', 'saved')"

    if rating and rating != "all":
        query += " AND i.rating = ?"
        params.append(rating)

    query += " ORDER BY i.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for r in rows:
        char_name = r["character_name"]
        filename = r["filename"]
        
        # Build media URLs
        thumb_url = f"/api/media/cache/{char_name}/thumb_{Path(filename).stem}.webp"
        temp_url = f"/api/media/temp/{char_name}/{filename}" if r["temp_path"] else None
        fav_url = f"/api/media/favorites/{char_name}/{filename}" if r["favorites_path"] else None

        results.append(ImageOut(
            id=r["id"],
            character_id=r["character_id"],
            filename=filename,
            rating=r["rating"] if "rating" in r.keys() and r["rating"] else "sfw",
            batch_number=r["batch_number"] if "batch_number" in r.keys() and r["batch_number"] else 1,
            task_id=r["task_id"] if "task_id" in r.keys() and r["task_id"] else None,
            temp_url=temp_url,
            favorites_url=fav_url,
            thumbnail_url=thumb_url,
            original_source=r["original_source"],
            source_url=r["source_url"],
            author_name=r["author_name"],
            author_url=r["author_url"],
            title=r["title"],
            copyright_info=r["copyright_info"],
            width=r["width"],
            height=r["height"],
            file_size=r["file_size"],
            phash=r["phash"],
            status=r["status"],
            download_time=str(r["download_time"]) if r["download_time"] else None,
            saved_time=str(r["saved_time"]) if r["saved_time"] else None
        ))
    return results

@router.post("/{image_id}/favorite")
async def save_favorite(image_id: int):
    ok = StorageService.save_favorite_image(image_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to save image to favorites")
    return {"status": "success", "message": f"Image {image_id} saved to favorites", "image_id": image_id}

@router.delete("/{image_id}/favorite")
async def remove_favorite(image_id: int, remove_file: bool = False):
    ok = StorageService.remove_favorite_image(image_id, remove_file=remove_file)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to remove image from favorites")
    return {"status": "success", "message": f"Image {image_id} removed from favorites", "image_id": image_id}

@router.api_route("/{image_id}/download", methods=["GET", "HEAD"])
async def download_original_image(image_id: int):
    """Serve the 100% original full-resolution master image with download header."""
    conn = get_connection()
    row = conn.execute("""
        SELECT i.*, c.name as character_name 
        FROM images i 
        JOIN characters c ON i.character_id = c.id 
        WHERE i.id = ?
    """, (image_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Image record not found")

    file_path = None
    if row["favorites_path"] and Path(row["favorites_path"]).exists():
        file_path = Path(row["favorites_path"])
    elif row["temp_path"] and Path(row["temp_path"]).exists():
        file_path = Path(row["temp_path"])

    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Original master file not found on disk")

    ext = file_path.suffix.lower() or ".jpg"
    download_filename = f"{row['character_name']}_{row['filename']}"
    
    media_type = "image/jpeg"
    if ext == ".png": media_type = "image/png"
    elif ext == ".webp": media_type = "image/webp"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=download_filename
    )

@router.post("/{image_id}/unfavorite")
async def unfavorite_image(image_id: int):
    """Removes an image from favorites and deletes the favorite master copy."""
    ok = StorageService.remove_from_favorites(image_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to remove from favorites")
    return {"status": "success", "message": "Image removed from favorites"}

@router.delete("/{image_id}")
async def delete_image(image_id: int):
    # If it was in favorites, remove favorite copy as well
    StorageService.remove_from_favorites(image_id)
    ok = StorageService.delete_single_image(image_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete image")
    return {"status": "success", "message": f"Image {image_id} deleted"}

@router.post("/batch")
async def batch_action(req: BatchActionRequest):
    if req.action == "save":
        success_count = sum(1 for img_id in req.image_ids if StorageService.save_favorite_image(img_id))
        return {"status": "success", "action": "save", "count": success_count}
    elif req.action == "unfavorite":
        success_count = sum(1 for img_id in req.image_ids if StorageService.remove_from_favorites(img_id))
        return {"status": "success", "action": "unfavorite", "count": success_count}
    elif req.action == "delete":
        success_count = 0
        for img_id in req.image_ids:
            StorageService.remove_from_favorites(img_id)
            if StorageService.delete_single_image(img_id):
                success_count += 1
        return {"status": "success", "action": "delete", "count": success_count}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown batch action: {req.action}")

# Media Streaming Router
media_router = APIRouter(prefix="/api/media", tags=["Media"])

@media_router.api_route("/{folder_type}/{character_name}/{filename}", methods=["GET", "HEAD"])
async def serve_media(folder_type: str, character_name: str, filename: str):
    if folder_type == "temp":
        base_dir = TEMP_DIR
    elif folder_type == "favorites":
        base_dir = FAVORITES_DIR
    elif folder_type == "cache":
        base_dir = CACHE_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid folder type")

    file_path = base_dir / character_name.strip() / filename
    if not file_path.exists():
        # Fallback for thumbnails if not yet generated or different ext
        if folder_type == "cache":
            # Check temp original as fallback
            orig_file = TEMP_DIR / character_name.strip() / f"{filename.replace('thumb_', '').replace('.webp', '.jpg')}"
            if orig_file.exists():
                return FileResponse(str(orig_file), media_type="image/jpeg")
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "image/webp" if filename.endswith(".webp") else "image/jpeg"
    if filename.endswith(".png"): media_type = "image/png"

    # Add cache headers for super fast browser response
    headers = {"Cache-Control": "public, max-age=86400, immutable"}
    return FileResponse(str(file_path), media_type=media_type, headers=headers)
