from fastapi import APIRouter, HTTPException
from typing import List, Optional
from database import get_connection
from models import CharacterOut

router = APIRouter(prefix="/api/characters", tags=["Characters"])

@router.get("", response_model=List[CharacterOut])
async def list_characters():
    conn = get_connection()
    rows = conn.execute("""
        SELECT 
            c.id, c.name, c.slug, c.avatar_url, c.created_at, c.last_searched_at,
            (SELECT COUNT(*) FROM images WHERE character_id = c.id AND status IN ('pending', 'saved')) as total_candidates,
            (SELECT COUNT(*) FROM images WHERE character_id = c.id AND status = 'saved') as total_favorites
        FROM characters c
        ORDER BY c.last_searched_at DESC, c.id DESC
    """).fetchall()
    conn.close()

    results = []
    for r in rows:
        avatar = r["avatar_url"]
        if avatar and "/data/anime-gallery/cache/" in avatar:
            avatar = avatar.replace("/data/anime-gallery/cache/", "/api/media/cache/")
        elif avatar and "/data/anime-gallery/temp/" in avatar:
            avatar = avatar.replace("/data/anime-gallery/temp/", "/api/media/temp/")
        elif avatar and "/data/anime-gallery/favorites/" in avatar:
            avatar = avatar.replace("/data/anime-gallery/favorites/", "/api/media/favorites/")

        results.append(CharacterOut(
            id=r["id"],
            name=r["name"],
            slug=r["slug"],
            avatar_url=avatar,
            created_at=str(r["created_at"]),
            last_searched_at=str(r["last_searched_at"]) if r["last_searched_at"] else None,
            total_candidates=r["total_candidates"],
            total_favorites=r["total_favorites"]
        ))
    return results

@router.get("/{name_or_id}")
async def get_character(name_or_id: str):
    conn = get_connection()
    if name_or_id.isdigit():
        row = conn.execute("SELECT * FROM characters WHERE id = ?", (int(name_or_id),)).fetchone()
    else:
        row = conn.execute("SELECT * FROM characters WHERE name = ? OR slug = ?", (name_or_id, name_or_id)).fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Character not found")

    char_id = row["id"]
    cand_count = conn.execute("SELECT COUNT(*) FROM images WHERE character_id = ? AND status IN ('pending', 'saved')", (char_id,)).fetchone()[0]
    fav_count = conn.execute("SELECT COUNT(*) FROM images WHERE character_id = ? AND status = 'saved'", (char_id,)).fetchone()[0]
    conn.close()

    return {
        "id": row["id"],
        "name": row["name"],
        "slug": row["slug"],
        "avatar_url": row["avatar_url"],
        "created_at": str(row["created_at"]),
        "last_searched_at": str(row["last_searched_at"]) if row["last_searched_at"] else None,
        "total_candidates": cand_count,
        "total_favorites": fav_count
    }

@router.delete("/{char_id}")
async def delete_character(char_id: int, delete_favorites: bool = False):
    from services.storage_service import StorageService
    res = StorageService.cleanup_character_space(char_id, delete_favorites=delete_favorites)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail="Character not found")
    return res
