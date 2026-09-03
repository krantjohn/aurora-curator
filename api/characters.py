from fastapi import APIRouter, HTTPException
from typing import List, Optional
from database import get_connection
from models import CharacterOut

router = APIRouter(prefix="/api/characters", tags=["Characters"])

@router.get("", response_model=List[CharacterOut])
async def list_characters(game: Optional[str] = None):
    conn = get_connection()
    # ONLY return characters that have actually been crawled and have at least 1 candidate or saved image
    query = """
        SELECT 
            c.id, c.name, c.slug, c.avatar_url, c.game, c.aliases, c.created_at, c.last_searched_at,
            (SELECT COUNT(*) FROM images WHERE character_id = c.id AND status IN ('pending', 'saved')) as total_candidates,
            (SELECT COUNT(*) FROM images WHERE character_id = c.id AND status = 'saved') as total_favorites,
            (SELECT thumbnail_path FROM images WHERE character_id = c.id AND thumbnail_path IS NOT NULL ORDER BY status = 'saved' DESC, id DESC LIMIT 1) as cover_thumb
        FROM characters c
        WHERE (SELECT COUNT(*) FROM images WHERE character_id = c.id AND status IN ('pending', 'saved')) > 0
    """
    params = []
    if game and game.lower() != "all":
        query += " AND c.game = ?"
        params.append(game.lower())
    
    query += " ORDER BY total_favorites DESC, total_candidates DESC, c.last_searched_at DESC, c.id ASC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for r in rows:
        avatar = r["cover_thumb"] or r["avatar_url"]
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
            game=r["game"] if "game" in r.keys() and r["game"] else "other",
            aliases=r["aliases"] if "aliases" in r.keys() else None,
            avatar_url=avatar,
            created_at=str(r["created_at"]),
            last_searched_at=str(r["last_searched_at"]) if r["last_searched_at"] else None,
            total_candidates=r["total_candidates"],
            total_favorites=r["total_favorites"]
        ))
    return results

@router.get("/catalog")
async def get_game_catalog(game: Optional[str] = None):
    """
    Returns the comprehensive character catalog for the 3 games with live crawl status.
    This powers the side-dock game roster selector modal.
    """
    from services.character_catalog import CHARACTER_CATALOG
    conn = get_connection()
    crawled_rows = conn.execute("""
        SELECT 
            c.id, c.name, c.avatar_url,
            (SELECT COUNT(*) FROM images WHERE character_id = c.id AND status IN ('pending', 'saved')) as total_candidates,
            (SELECT COUNT(*) FROM images WHERE character_id = c.id AND status = 'saved') as total_favorites,
            (SELECT thumbnail_path FROM images WHERE character_id = c.id AND thumbnail_path IS NOT NULL ORDER BY status = 'saved' DESC, id DESC LIMIT 1) as cover_thumb
        FROM characters c
    """).fetchall()
    conn.close()

    crawled_map = {r["name"]: r for r in crawled_rows}

    catalog = []
    for item in CHARACTER_CATALOG:
        if game and game.lower() != "all" and item["game"] != game.lower():
            continue
        
        name = item["name"]
        crawled_info = crawled_map.get(name)
        has_crawled = bool(crawled_info and (crawled_info["total_candidates"] > 0 or crawled_info["total_favorites"] > 0))
        
        cover = None
        if crawled_info and crawled_info["cover_thumb"]:
            cover = crawled_info["cover_thumb"]
        elif crawled_info and crawled_info["avatar_url"] and not crawled_info["avatar_url"].startswith("/static/"):
            cover = crawled_info["avatar_url"]
        else:
            cover = f"/static/avatars/{item['slug']}.svg"
            
        if cover and "/data/anime-gallery/cache/" in cover:
            cover = cover.replace("/data/anime-gallery/cache/", "/api/media/cache/")
        elif cover and "/data/anime-gallery/temp/" in cover:
            cover = cover.replace("/data/anime-gallery/temp/", "/api/media/temp/")
        elif cover and "/data/anime-gallery/favorites/" in cover:
            cover = cover.replace("/data/anime-gallery/favorites/", "/api/media/favorites/")

        catalog.append({
            "name": item["name"],
            "slug": item["slug"],
            "game": item["game"],
            "game_name": item.get("game_name", "游戏角色"),
            "aliases": item.get("aliases", []),
            "accent_color": item.get("accent_color", "#c5a880"),
            "avatar_url": cover,
            "is_crawled": has_crawled,
            "total_candidates": crawled_info["total_candidates"] if crawled_info else 0,
            "total_favorites": crawled_info["total_favorites"] if crawled_info else 0
        })
        
    return catalog

@router.post("/seed")
async def seed_characters_endpoint():
    from database import cleanup_empty_characters, sync_crawled_characters_metadata
    cleanup_empty_characters()
    sync_crawled_characters_metadata()
    return {"status": "ok", "message": "Cleaned up un-crawled characters and synced metadata"}

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
