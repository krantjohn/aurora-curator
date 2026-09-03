from fastapi import APIRouter, HTTPException
from services.storage_service import StorageService

router = APIRouter(prefix="/api/storage", tags=["Storage"])

@router.post("/clean-temp/{character_name}")
async def clean_character_temp_candidates(character_name: str):
    """
    CRITICAL: Cleans temporary candidate files for the given character,
    preserving all favorited images in /data/anime-gallery/favorites/<character_name>/.
    """
    char_clean = character_name.strip()
    if not char_clean:
        raise HTTPException(status_code=400, detail="Character name required")

    result = StorageService.clean_character_temp(char_clean)
    return {
        "status": "success",
        "message": f"已成功清理【{char_clean}】的所有临时图片（共 {result['cleaned_temp_count']} 张），已收藏的图片已安全保留！",
        "details": result
    }

from fastapi.responses import FileResponse
from config import CACHE_DIR

@router.get("/stats")
async def get_storage_stats():
    return StorageService.get_storage_stats()

@router.get("/export-zip")
async def export_favorites_zip():
    """Packages all favorites into a downloadable zip file for easy backup/Google Photos import."""
    zip_path = CACHE_DIR / "anime_favorites_backup.zip"
    StorageService.export_favorites_zip(zip_path)
    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename="anime_favorites_all.zip"
    )
